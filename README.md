# blaine-morgan.github.io

Marketing site for Blaine Morgan's custom business apps. Static: `index.html` +
`style.css`, no build step, served by GitHub Pages from `main` at
https://blaine-morgan.github.io/.

Every call to action points at the Instant Business Demo funnel served by BlaineOS
(`https://blaine-home-2.tail993575.ts.net:8443/instant-business-demo/?ref=site`),
the same page the business-card QR opens. The site is separate from BlaineOS on
purpose: it stays up when the Windows PC that runs BlaineOS does not, and it ships
on its own cadence. See [`docs/SITE.md`](docs/SITE.md) for the structure, the copy
rules and the claims to confirm before the cards are printed.

Documentation index: [`docs/INDEX.md`](docs/INDEX.md) / [`docs/INDEX.json`](docs/INDEX.json).
Run `python3 scripts/check-docs.py` after any documentation change; CI enforces it.

## Change the copy

Edit `index.html`. Keep the demo URL identical in every CTA (search `ref=site`).
Nothing on the page may claim a client, a number or a testimonial that is not real.

## Custom domain (later)

Add a `CNAME` file containing the domain, point the domain's DNS at GitHub Pages,
and set `publicGatewayUrl` in BlaineOS Settings if the demo moves behind it too.
