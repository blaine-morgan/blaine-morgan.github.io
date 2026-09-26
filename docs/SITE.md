---
id: SITE
genre: reference
status: current
updated: 2026-09-26
summary: Structure of the marketing page (V2 Bold design), its primary CTA (the demo request that is saved and built in the background, link sent by email/text), the walkthrough ask, the design tokens, the copy rules, and what Blaine still has to supply.
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
| Hero | "Your whole business. One screen." Three rotated overnight cards show what an automated morning looks like | See your demo in two minutes → `#demo`; "See how it works" → `#how` |
| Industry strip | Amber marquee of industries (pauses and wraps under `prefers-reduced-motion`) | none |
| Sound familiar? | Sticky headline, numbered 01/02/03 pains | none |
| What we do · 01 | Navy: "Automate the busywork", Estimate → Job → Invoice → Paid flow, three bullets | none |
| What we do · 02 | Paper: "See it all in one place", bar chart, three bullets | "Try a two-minute sample demo" → `#demo` |
| Promise band | 1 screen / 0 numbers typed twice / same-day reply | none |
| How it works | Three triangle-marked steps: free walkthrough 45 min, we build it 2–4 weeks, handoff & support | none |
| About | "A neighbor who speaks both languages", the mountain mark in place of a photo until Blaine supplies one | none |
| Demo intake (`#demo`) | The four demo questions plus name, email, optional phone | Show me my demo → confirmation on the page; link arrives by email/text |
| Walkthrough (`#contact`) | The secondary ask; routes through the demo request until a business email exists | Request your demo and mention a walkthrough |
| Footer | Wordmark, anchors, copyright | none |

The pull quote section is commented out until a real client quote exists.

## The demo intake

The form at `#demo` collects the four demo questions plus name, email and an
optional phone, and posts them as JSON to
`POST …/instant-business-demo/submit` on the public gateway (CORS for this origin).
The service saves the lead, answers 202 at once and builds the demo in a durable
background queue that retries through provider outages; when the demo is ready
BlaineOS emails the link (and texts it when a phone was given and Twilio is
configured), or notifies Blaine to send it by hand when email is not configured.
The visitor sees only a confirmation on this page ("Got it. We'll email the link…");
nobody is sent to the BlaineOS demo page, which remains only as what the emailed
link opens (`/d/<token>`) and as the business-card QR target. On a service error
the page retries once, then asks the visitor to try again; nothing is stored on the site.

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

## What Blaine still has to supply

No bracketed placeholders remain. To finish the page:

1. A business email (and optionally a phone): then the walkthrough section gets a
   real "email us" button and the about section its "You'll have my number" line
   becomes literal. Nothing on the page today invents an address.
2. A photo for the about section (replaces the mountain mark in `about-photo`).
3. A real client quote for the pull quote section (uncomment it in `index.html`).
4. The about copy's one-line background sentence, if the current wording is off.

Claims on the page Blaine has not confirmed: "2–4 weeks", "fixed price, agreed up
front", "we reply within one business day", "45 minutes, no pitch", "about a minute"
for the demo build.

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
