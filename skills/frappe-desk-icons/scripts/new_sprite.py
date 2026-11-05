#!/usr/bin/env python3
"""Start a duotone sprite for an app that has none, with its palette and a Home icon.

Usage: new_sprite.py <app repo> --body <hex> --detail <hex> [--dark-body <hex>] [--dark-detail <hex>]
                     [--brand "the logo's green"]

body is the big light shape, detail the small dark one, both taken from the app's logo. The dark
theme needs its own pair (a deep body, a light detail) because a dark detail vanishes on the
dark tray; when omitted they are derived. Active colours are derived by darkening.
"""

import argparse
import colorsys
import os


def shade(hex_color, lightness):
	r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
	h, l, s = colorsys.rgb_to_hls(r, g, b)
	r, g, b = colorsys.hls_to_rgb(h, max(0, min(1, l + lightness)), s)
	return "#%02x%02x%02x" % tuple(round(c * 255) for c in (r, g, b))


TEMPLATE = """<!-- {title}'s dual-tone module icons for the desk dock, sidebars and headers. Each symbol animates
     while its dock tile is hovered, through the icon-motion custom properties the tile sets
     (frappe/public/scss/desk/dock.scss): `icon-motion` (paused | running) and
     `icon-motion-opacity` (0 | 1).

     A name must end in `-duotone` for the dock to draw it on the 24px grid with the tile's tones.
     Every id, class and custom property is prefixed `{p}-` so nothing clashes with another app's
     sprite.

     This sprite is inserted into the page, so the style block below is a document stylesheet. -->

<svg id="{p}-module-symbols" aria-hidden="true" style="display: none;" class="icon" xmlns="http://www.w3.org/2000/svg">
	<style>
		/* The {title} colours, from {brand}: the body of a shape and its detail. light-dark() picks
		   per theme; the dark theme uses a deep body and a light detail so the pair reads on a dark tray.
		     rest     light: {body} / {detail}     dark: {dbody} / {ddetail}
		     active   light: {abody} / {adetail}     dark: {adbody} / {addetail} */
		:root {{
			--{p}-body: light-dark({body}, {dbody});
			--{p}-detail: light-dark({detail}, {ddetail});
			--{p}-body-active: light-dark({abody}, {adbody});
			--{p}-detail-active: light-dark({adetail}, {addetail});
		}}
		/* Frappe's sprite sets grey tones on every duotone tile and header. These win for {title}'s
		   icons only, through the symbol the tile holds, so other apps keep their own. */
		.dock-item--duotone:has(use[href^="#icon-{p}-"]),
		.shell-header:hover .header-logo:has(use[href^="#icon-{p}-"]),
		.shell-header.hover .header-logo:has(use[href^="#icon-{p}-"]) {{
			--duotone-light: var(--{p}-body);
			--duotone-dark: var(--{p}-detail);
		}}
		.dock-item--duotone.active:has(use[href^="#icon-{p}-"]) {{
			--duotone-light: var(--{p}-body-active);
			--duotone-dark: var(--{p}-detail-active);
		}}

		/* Home: the front door swings open on its left hinge. */
		.{p}-door {{
			transform-box: fill-box;
			transform-origin: left center;
			transform: scaleX(calc(1 - 0.7 * var(--icon-motion-opacity, 0)));
			transition: transform 0.3s ease;
		}}
	</style>

	<!-- Home: a house with a door. -->
	<symbol viewBox="0 0 24 24" id="icon-{p}-home-duotone" stroke="none" style="overflow: visible">
		<path d="M4.5 10.2 12 4.3l7.5 5.9V20a1.5 1.5 0 0 1-1.5 1.5H6A1.5 1.5 0 0 1 4.5 20z" style="fill: var(--duotone-light, var(--{p}-body))" />
		<path d="M2.6 11 12 3.3l9.4 7.7" style="fill: none; stroke: var(--duotone-dark, var(--{p}-detail)); stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round" />
		<rect class="{p}-door" x="9.8" y="14" width="4.4" height="7.5" rx="1" style="fill: var(--duotone-dark, var(--{p}-detail))" />
	</symbol>
</svg>
"""


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("repo")
	parser.add_argument("--body", required=True)
	parser.add_argument("--detail", required=True)
	parser.add_argument("--dark-body")
	parser.add_argument("--dark-detail")
	parser.add_argument("--brand", default="the logo")
	args = parser.parse_args()

	repo = os.path.abspath(os.path.expanduser(args.repo))
	app = os.path.basename(repo)
	out = os.path.join(repo, app, "public", "icons", "module-icons.svg")
	if os.path.exists(out):
		raise SystemExit(f"{out} exists; add symbols to it instead")

	dbody = args.dark_body or shade(args.body, -0.3)
	ddetail = args.dark_detail or shade(args.body, 0.35)
	os.makedirs(os.path.dirname(out), exist_ok=True)
	with open(out, "w") as f:
		f.write(TEMPLATE.format(
			p=app, title=app.replace("_", " ").title(), brand=args.brand,
			body=args.body, detail=args.detail, dbody=dbody, ddetail=ddetail,
			abody=shade(args.body, -0.08), adetail=shade(args.detail, -0.08),
			adbody=shade(dbody, 0.06), addetail=shade(ddetail, 0.06),
		))
	print(f"wrote {out}")
	print(f'add to {app}/hooks.py: app_include_icons = ["/assets/{app}/icons/module-icons.svg"]')


if __name__ == "__main__":
	main()
