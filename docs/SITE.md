---
id: SITE
genre: reference
status: current
updated: 2026-09-25
summary: Structure of the marketing page (V2 Bold design), its primary CTA (the walkthrough form) and the demo funnel link, the design tokens, the copy rules, and the bracketed placeholders Blaine must fill before launch.
---

# The marketing site

One page, static, served by GitHub Pages at https://morgantechconsulting.com/.
Since 2026-09-25 it is the "V2 Bold" design from Blaine's design canvas
(claude.ai artifact `XKQKZCjZwX2k9KaQsJKkEB`, boards `Bold.dc.html` desktop 1440 and
`BoldMobile.dc.html` phone 390). Its job is to book a free 45-minute walkthrough;
the Instant Business Demo funnel (BlaineOS, `docs/business-demo.md` there) is offered
as a secondary link inside the "See it all in one place" block.

## Sections, in order

| Section | Purpose | CTA |
| --- | --- | --- |
| Hero | "Your whole business. One screen." Three rotated overnight cards show what an automated morning looks like | Book a free walkthrough → `#contact`; "See how it works" → `#how` |
| Industry strip | Amber marquee of industries (pauses and wraps under `prefers-reduced-motion`) | none |
| Sound familiar? | Sticky headline, numbered 01/02/03 pains: numbers in five places, typed twice, found out too late | none |
| What we do · 01 | Navy: "Automate the busywork", Estimate → Job → Invoice → Paid flow, three bullets | none |
| What we do · 02 | Paper: "See it all in one place", bar chart, three bullets | Demo funnel link (secondary) |
| Promise band | 1 screen / 0 numbers typed twice / same-day reply | none |
| How it works | Three triangle-marked steps: free walkthrough 45 min, we build it 2–4 weeks, handoff & support | none |
| Pull quote | Client quote placeholder on navy | none |
| About | "A neighbor who speaks both languages", photo placeholder | none |
| Contact | Form: name, company, email or phone, message | Book my free walkthrough |
| Footer | Wordmark, anchors, copyright | none |

## Primary CTA and the form

GitHub Pages runs no server, so the contact form submits with `action="mailto:…"`
(`method="get"`, `enctype="text/plain"`): the visitor's mail client opens with the
fields prefilled. Replace `hello@example.com` in the form `action` and the email link
with the real address before launch. If a real form backend is wanted later (Formspree,
a BlaineOS route on the public gateway), change only the `<form>` element.

## Funnel link

`https://blaine-home-2.tail993575.ts.net:8443/instant-business-demo/?ref=site`, one
link in the "See it all in one place" block. BlaineOS records `site` as a referral kind.
If `publicGatewayUrl` changes, change this link.

## Design language

Tokens from the canvas build note, all in `:root` in `style.css`:

| Token | Value | Used for |
| --- | --- | --- |
| navy | `#08203D` | hero, quote, contact |
| navy-2 | `#0D2A4D` | services block, headings |
| footer | `#061729` | footer |
| amber | `#F0A030` | CTA, bands, markers (navy text on it) |
| amber-ink | `#B4560F` | labels on light backgrounds |
| paper | `#F2EFE8` | second services block, photo frame |
| text / muted | `#1F2937` / `#4B5563` | body copy |

Type: Archivo 900 uppercase for display (H1 104 px desktop / 58 px phone, H2 60 / 40,
letter-spacing -0.03em, line-height ≈0.96); Source Sans 3 18–20 px body; 13 px 800
0.18em uppercase labels. Both come from Google Fonts (the only external requests).
Motifs: the two-peak mountain mark (inline SVG paths, bleeding off section edges),
solid triangles as bullets and step markers, full-bleed amber bands, corners ≤ 12 px,
no bordered cards, no shadows. The three hero cards are rotated -2° / 1.5° / -1°.
`logo.svg` is the white wordmark from the canvas; it only sits on navy.
Phone layout (≤ 760 px) mirrors the mobile board: hamburger menu (CSS checkbox, no
script), stacked cards, single-column steps and promises, 20 px gutter, no horizontal
scroll.

## Copy rules

- No clients, logos, testimonials, counts or savings figures unless they are real
  and Blaine supplied them. The hero cards and the bar chart are illustrative.
- The demo uses sample data; say so wherever the demo is offered.
- Plain sentences, second person, no AI vocabulary.
- Bracketed text is a placeholder and must be replaced before the site is promoted.

## Placeholders to fill before launch

All are literal `[...]` strings in `index.html`; search for `[`.

1. `[YOUR TOWN], [STATE]` in the hero pill, the about copy and the footer.
2. `[Your Name]` in the about copy and the photo caption; the background sentence.
3. `[Photo of you on a job site — real, not stock]`: drop a photo into the `about-photo` figure.
4. The client quote, `[Name]`, `[Title], [Company] · [Town]`, or remove the quote section.
5. `[Your phone]` / `[Your email]` and the `tel:` / `mailto:` hrefs beside them.
6. `hello@example.com` in the form `action`.

Claims on the page that Blaine has not confirmed: "2–4 weeks", "fixed price, agreed
up front", "we reply within one business day", "45 minutes, no pitch".

## Domain

`morgantechconsulting.com` (registrar GoDaddy, nameservers `ns15/ns16.domaincontrol.com`).
`CNAME` in the repo root names it and the Pages setting carries it, so GitHub serves
the site there once DNS points at Pages. Records Blaine sets at GoDaddy (2026-09-24):

| Host | Type | Value |
| --- | --- | --- |
| `@` | A | `185.199.108.153` |
| `@` | A | `185.199.109.153` |
| `@` | A | `185.199.110.153` |
| `@` | A | `185.199.111.153` |
| `www` | CNAME | `blaine-morgan.github.io` |

Remove GoDaddy's parking records first (today `@` A `76.223.105.230` / `13.248.243.5`,
`www` CNAME to the apex). Verify: `curl -sI https://morgantechconsulting.com/ | head -1`
returns 200 and the Pages setting shows the certificate issued; then turn on "Enforce
HTTPS" (`gh api -X PUT repos/blaine-morgan/blaine-morgan.github.io/pages -F https_enforced=true`).
`https://blaine-morgan.github.io/` keeps redirecting to the domain.

## Deploy

Push to `main`. GitHub Pages serves the root of the branch (`.nojekyll` present).
Check `https://morgantechconsulting.com/` returns the new `<title>` within a minute
or two. The docs workflow runs `scripts/check-docs.py` on every push.
