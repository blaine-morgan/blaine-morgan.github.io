---
id: SITE
genre: reference
status: current
updated: 2026-09-23
summary: Structure of the marketing page, the funnel it feeds, the design language shared with the demo page, the copy rules, and the claims Blaine must confirm before the business cards go out.
---

# The marketing site

One page, static, served by GitHub Pages at https://blaine-morgan.github.io/.
Its only job is to send a visitor into the Instant Business Demo funnel
(BlaineOS, `docs/business-demo.md` there) with enough context that the four
questions make sense.

## Sections, in order

| Section | Purpose | CTA |
| --- | --- | --- |
| Hero | The promise (the task done by hand should run itself) and an example of what the demo builds | Build my demo |
| Where the hours go | Names the three costs a visitor recognises: re-keying, chasing, the spreadsheet-as-system | none |
| How it works | The funnel as five numbered steps: questions, demo, feedback, prototype, real app | Start with the four questions |
| What I build | Six task types, phrased as outcomes, not product names | none |
| Why it costs less | One builder, an automated build pipeline, single-task scope | none |
| Questions | Six FAQs, the objections before scanning a card | none |
| Start here | Final CTA | Build my demo |

## Funnel link

`https://blaine-home-2.tail993575.ts.net:8443/instant-business-demo/?ref=site`.
BlaineOS records every visit; today anything other than `ref=business-card` is
counted as `direct`, so site visits are not yet distinguishable from typed-in ones.
Add `site` as a referral kind in BlaineOS (`server/business-demo.mjs`, `recordVisit`)
when that distinction matters. If `publicGatewayUrl` changes, change every CTA here.

## Design language

Shared with the demo page (`blaineos/public-business-demo/style.css`) so the
scan-to-demo path feels like one place: cream canvas `#f5f1e8`, paper cards,
ink `#182723`, forest green `#2e6245`, Georgia display, monospace eyebrows,
hairline borders, numbered rails. No webfonts, no scripts, no images; the page is
two files. The hero "ticket" mirrors the four questions in the order the form asks
them. Works at phone width with a 16 px gutter and no horizontal scroll.

## Copy rules

- No clients, logos, testimonials, counts or savings figures unless they are real
  and Blaine supplied them. The hero example is labelled as an example.
- The demo uses sample data; say so wherever the demo is offered.
- Every CTA is the same link. The site collects nothing itself.
- Plain sentences, second person, no AI vocabulary.

## Claims to confirm before printing cards

These are on the page today and are reasonable, but Blaine has not stated them:

1. "A prototype for a single, well-described task follows within days."
2. "The demo and the feedback step are free. Price comes with the scope, after the prototype."
3. "Fixed scope" for the real app.
4. "Nothing is shared or sold" about the visitor's answers.

Change the wording in `index.html` if any of these is not how Blaine wants to work.

## Deploy

Push to `main`. GitHub Pages serves the root of the branch (`.nojekyll` present).
Check `https://blaine-morgan.github.io/` returns the new `<title>` within a minute
or two. The docs workflow runs `scripts/check-docs.py` on every push.
