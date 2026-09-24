#!/usr/bin/env python3
"""Documentation contract checker.

Machine-enforced invariants for the doc set. Optimized for agent consumption:
every doc carries typed frontmatter, every doc is reachable, every link resolves,
and INDEX.json is a faithful projection of the filesystem.

Usage:
    python3 scripts/check-docs.py            # check, exit 1 on error
    python3 scripts/check-docs.py --json     # machine-readable report
    python3 scripts/check-docs.py --reindex  # rewrite doc/INDEX.json from frontmatter

Checks:
  L1 every relative markdown link resolves (repo-local or sibling repo)
  L2 every backtick-quoted *.md reference resolves, or is declared in
     frontmatter `external_refs` with a retrieval note
  F1 every doc under the doc root has YAML frontmatter
  F2 frontmatter carries required keys with values from the allowed enums
  F3 `updated` parses as an ISO date and is not in the future
  I1 INDEX.json lists exactly the docs present on disk
  I2 INDEX.json fields agree with each file's frontmatter
  R1 every doc is reachable from an entrypoint (README/AGENTS) via links
  S1 docs with status: current are not older than STALE_DAYS
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOME = REPO.parent

# --- contract -------------------------------------------------------------

GENRES = {
    "reference",    # describes the system as it is
    "direction",    # confirmed user intent, not yet fully built
    "requirements", # numbered delivery obligations
    "tracker",      # delivery status, mutable
    "audit",        # independent assessment
    "runbook",      # operational procedure
    "increment",    # one changeset receipt, immutable once written
    "history",      # archived dated log entries
    "index",        # catalog
}

STATUSES = {
    "current",      # describes present reality / active intent
    "historical",   # accurate when written, retained as history
    "superseded",   # replaced by a named successor
}

REQUIRED = ("id", "genre", "status", "updated")
STALE_DAYS = 45

DOC_DIRS = ("doc", "docs")
ENTRYPOINTS = ("README.md", "AGENTS.md")

# Repositories in this estate. A reference whose first segment names one of these
# is a cross-repo pointer: legitimate, and unresolvable from a single checkout.
# CI checks out one repository, so these are verified only when the sibling exists
# locally. Without this, every cross-repo reference fails in CI and the workflow
# emails on every push while nothing is actually wrong.
SIBLING_REPOS = ("opencode-supervisor", "blaineos", "blaineIDE", "friday-apple")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MD_TICK = re.compile(r"`([A-Za-z0-9._/-]+\.md)`")
ISO = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")


def doc_root(repo: Path) -> Path | None:
    for name in DOC_DIRS:
        if (repo / name).is_dir():
            return repo / name
    return None


def exempt_paths(repo: Path) -> set[str]:
    """Repo-relative paths excused from the frontmatter requirement.

    For files consumed verbatim at runtime (e.g. an OpenCode `instructions`
    file), frontmatter would be injected into every agent prompt. List those in
    <docroot>/.check-docs-exempt, one path per line.
    """
    root = doc_root(repo)
    if root is None:
        return set()
    f = root / ".check-docs-exempt"
    if not f.exists():
        return set()
    return {ln.strip() for ln in f.read_text().split("\n")
            if ln.strip() and not ln.lstrip().startswith("#")}


def parse_frontmatter(text: str) -> dict | None:
    """Minimal YAML subset: scalars, inline lists, comments. No nesting."""
    m = FRONTMATTER.match(text)
    if not m:
        return None
    data: dict = {}
    for line in m.group(1).split("\n"):
        line = line.split(" #", 1)[0].rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key, raw = key.strip(), raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            data[key] = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
        else:
            data[key] = raw.strip("\"'")
    return data


def body_of(text: str) -> str:
    m = FRONTMATTER.match(text)
    return text[m.end():] if m else text


def iter_docs(repo: Path):
    """Every tracked markdown file, excluding vendored and runtime trees."""
    skip = ("/node_modules/", "/.git/", "/.local/", "/dist/", "/__pycache__/")
    for p in sorted(repo.rglob("*.md")):
        s = str(p)
        if any(x in s for x in skip):
            continue
        yield p


def safe_exists(p: Path) -> bool:
    try:
        return p.exists()
    except OSError:
        return False


def resolve(src: Path, target: str, repo: Path) -> bool:
    t = target.split("#", 1)[0].strip()
    if not t or t.startswith(("http://", "https://", "mailto:", "tel:")):
        return True
    if t.startswith("/"):
        return safe_exists(Path(t))
    if safe_exists(src.parent / t):
        return True
    # sibling-repo layout: `opencode-supervisor/doc/X.md` from another checkout
    return safe_exists(HOME / t)


def check(repo: Path) -> dict:
    root = doc_root(repo)
    errors: list[str] = []
    warnings: list[str] = []
    docs = list(iter_docs(repo))
    exempt = exempt_paths(repo)
    fm_by_path: dict[Path, dict] = {}

    for p in docs:
        text = p.read_text(errors="replace")
        rel = p.relative_to(repo)
        in_docroot = (root is not None and root in p.parents
                      and str(rel) not in exempt)

        # L1
        for target in MD_LINK.findall(text):
            if not resolve(p, target, repo):
                errors.append(f"L1 {rel}: broken link -> {target}")

        fm = parse_frontmatter(text)
        if in_docroot:
            if fm is None:
                errors.append(f"F1 {rel}: missing frontmatter")
            else:
                fm_by_path[p] = fm
                for key in REQUIRED:
                    if key not in fm:
                        errors.append(f"F2 {rel}: frontmatter missing '{key}'")
                if fm.get("genre") not in GENRES and "genre" in fm:
                    errors.append(f"F2 {rel}: genre '{fm['genre']}' not in {sorted(GENRES)}")
                if fm.get("status") not in STATUSES and "status" in fm:
                    errors.append(f"F2 {rel}: status '{fm['status']}' not in {sorted(STATUSES)}")
                upd = fm.get("updated", "")
                if not ISO.match(str(upd)):
                    errors.append(f"F3 {rel}: updated '{upd}' is not YYYY-MM-DD")
                else:
                    d = dt.date.fromisoformat(upd)
                    # One day of slack for timezone skew. The Pi runs MDT and CI
                    # runs UTC, so a doc dated "today" in UTC looks like tomorrow
                    # on the Pi. Without this the same commit passes in CI and
                    # fails locally every evening.
                    if d > dt.date.today() + dt.timedelta(days=1):
                        errors.append(f"F3 {rel}: updated {upd} is in the future")
                    elif fm.get("status") == "current":
                        age = (dt.date.today() - d).days
                        if age > STALE_DAYS:
                            warnings.append(f"S1 {rel}: status current but {age}d old")

        # L2 — backticked filenames must resolve or be declared external
        declared = set(fm.get("external_refs", []) if fm else [])
        for ref in MD_TICK.findall(body_of(text)):
            # absolute paths are machine locations, not repo references
            if ref.startswith("/") or ref in declared or "JOB_ID" in ref or "vN" in ref:
                continue
            # Cross-repo pointer: verify only when that sibling is checked out.
            head = ref.split("/", 1)[0]
            if head in SIBLING_REPOS and head != repo.name and not safe_exists(HOME / head):
                continue
            cands = [p.parent / ref, repo / ref, HOME / ref]
            if root is not None:
                cands += [root / ref, root / "increments" / ref, root / "history" / ref]
            for sib in ("blaineIDE", "blaineos", "opencode-supervisor"):
                cands += [HOME / sib / ref, HOME / sib / "doc" / ref, HOME / sib / "docs" / ref]
            if not any(safe_exists(c) for c in cands):
                errors.append(
                    f"L2 {rel}: `{ref}` not found and not declared in external_refs"
                )

    # I1/I2 — index agrees with disk
    if root is not None:
        index_path = root / "INDEX.json"
        if not index_path.exists():
            errors.append(f"I1 {index_path.relative_to(repo)}: missing")
        else:
            index = json.loads(index_path.read_text())
            listed = {e["path"] for e in index["docs"]}
            on_disk = {
                str(p.relative_to(repo)) for p in fm_by_path
                if p.name != "INDEX.json"
            }
            for missing in sorted(on_disk - listed):
                errors.append(f"I1 INDEX.json: {missing} on disk but not indexed")
            for extra in sorted(listed - on_disk):
                errors.append(f"I1 INDEX.json: {extra} indexed but not on disk")
            by_path = {str(p.relative_to(repo)): fm for p, fm in fm_by_path.items()}
            for entry in index["docs"]:
                fm = by_path.get(entry["path"])
                if not fm:
                    continue
                for key in ("id", "genre", "status", "updated"):
                    if str(entry.get(key)) != str(fm.get(key)):
                        errors.append(
                            f"I2 INDEX.json: {entry['path']} {key}="
                            f"{entry.get(key)!r} but frontmatter has {fm.get(key)!r}"
                        )

    # R1 — reachability from entrypoints
    if root is not None:
        adj: dict[Path, set[Path]] = {}
        for p in docs:
            out = set()
            for target in MD_LINK.findall(p.read_text(errors="replace")):
                t = target.split("#", 1)[0].strip()
                if not t or t.startswith(("http", "mailto:", "tel:")):
                    continue
                q = (p.parent / t)
                try:
                    q = q.resolve()
                except OSError:
                    continue
                if safe_exists(q):
                    out.add(q)
            adj[p.resolve()] = out
        seen: set[Path] = set()
        stack = [(repo / e).resolve() for e in ENTRYPOINTS if (repo / e).exists()]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(adj.get(cur, ()))
        for p in sorted(fm_by_path):
            if p.resolve() not in seen:
                warnings.append(f"R1 {p.relative_to(repo)}: unreachable from {'/'.join(ENTRYPOINTS)}")

    return {"repo": str(repo), "errors": errors, "warnings": warnings,
            "docs": len(docs), "indexed": len(fm_by_path)}


def reindex(repo: Path) -> None:
    root = doc_root(repo)
    if root is None:
        return
    entries = []
    exempt = exempt_paths(repo)
    for p in iter_docs(repo):
        if (root not in p.parents or p.name == "INDEX.json"
                or str(p.relative_to(repo)) in exempt):
            continue
        fm = parse_frontmatter(p.read_text(errors="replace"))
        if not fm:
            continue
        entry = {
            "id": fm.get("id"),
            "path": str(p.relative_to(repo)),
            "genre": fm.get("genre"),
            "status": fm.get("status"),
            "updated": fm.get("updated"),
        }
        for opt in ("requirements", "supersedes", "superseded_by",
                    "authority", "summary", "external_refs"):
            if opt in fm:
                entry[opt] = fm[opt]
        entries.append(entry)
    # INDEX.md is generated below, so its own frontmatter must never feed the index:
    # on a first run it does not exist yet, and on any run where the newest doc date
    # has advanced its scanned `updated` is stale, which made INDEX.json and the
    # regenerated INDEX.md disagree until a second run. Derive its entry from the
    # other documents instead, so one run always converges.
    index_path = str((root / "INDEX.md").relative_to(repo))
    entries = [e for e in entries if e["path"] != index_path]
    entries.append({
        "id": "DOC-INDEX",
        "path": index_path,
        "genre": "index",
        "status": "current",
        "updated": max((e["updated"] for e in entries if e.get("updated")),
                       default=dt.date.today().isoformat()),
        "summary": "Catalog of every document, typed by genre and status."
                   " Entry point for agents.",
    })
    entries.sort(key=lambda e: (e["genre"] or "", e["id"] or ""))
    out = {
        "schema": 1,
        "generated_by": "scripts/check-docs.py --reindex",
        "repo": repo.name,
        "genres": sorted(GENRES),
        "statuses": sorted(STATUSES),
        "docs": entries,
    }
    (root / "INDEX.json").write_text(json.dumps(out, indent=2) + "\n")
    _write_catalog(root, entries)


GENRE_ORDER = ["direction", "requirements", "tracker", "audit", "reference",
               "runbook", "increment", "history", "index"]
GENRE_BLURB = {
    "direction": "Confirmed user intent. Target state, not an implementation claim.",
    "requirements": "Numbered delivery obligations and acceptance criteria.",
    "tracker": "Mutable delivery status. Current state only.",
    "audit": "Independent assessment. Binding where it contradicts a completion claim.",
    "reference": "How the system behaves now.",
    "runbook": "Operational procedure.",
    "increment": "One changeset receipt each, immutable once written. Read only for"
                 " the requirement named; never as current system description.",
    "history": "Archived dated entries. Never current state.",
    "index": "Catalogs.",
}


def _write_catalog(root: Path, entries: list) -> None:
    """Regenerate INDEX.md so the human-readable catalog cannot drift from disk."""
    # Derived from content, never wall-clock: a date that moved every day would
    # make the CI "index is current" check fail on any later run.
    newest = max((e["updated"] for e in entries if e.get("updated")),
                 default=dt.date.today().isoformat())
    out = ["---", "id: DOC-INDEX", "genre: index", "status: current",
           f"updated: {newest}",
           "summary: Catalog of every document, typed by genre and status."
           " Entry point for agents.",
           "---", "",
           "# Documentation index", "",
           "Generated by `scripts/check-docs.py --reindex`. Do not hand-edit.",
           "Machine-readable equivalent: [INDEX.json](INDEX.json). Every document",
           "carries `id`, `genre`, `status` and `updated` frontmatter; filter on those",
           "rather than reading whole files.", "",
           "**Genre determines how much authority a document has.** `direction` and",
           "`requirements` state intent; `reference` describes present behaviour;",
           "`audit` overrides completion claims; `increment` and `history` are dated",
           "receipts that must never be read as current state.", ""]
    by_genre: dict[str, list] = {}
    for e in entries:
        by_genre.setdefault(e["genre"], []).append(e)
    for g in GENRE_ORDER:
        if g not in by_genre:
            continue
        out += [f"## {g}", "", GENRE_BLURB.get(g, ""), "",
                "| Doc | Status | Updated | Summary |", "| --- | --- | --- | --- |"]
        for e in by_genre[g]:
            rel = os.path.relpath(Path(e["path"]), root.name)
            out.append(f"| [{e['id']}]({rel}) | {e['status']} | {e['updated']} "
                       f"| {e.get('summary', '')} |")
        out.append("")
    (root / "INDEX.md").write_text("\n".join(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--reindex", action="store_true")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("repo", nargs="?", default=str(REPO))
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    if args.reindex:
        reindex(repo)

    report = check(repo)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for e in report["errors"]:
            print(f"ERROR  {e}")
        for w in report["warnings"]:
            print(f"WARN   {w}")
        print(f"\n{report['docs']} docs, {report['indexed']} indexed, "
              f"{len(report['errors'])} errors, {len(report['warnings'])} warnings")
    bad = report["errors"] or (args.strict and report["warnings"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
