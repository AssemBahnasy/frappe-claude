#!/usr/bin/env python3
"""Check a Frappe app's duotone icon sprite and the icons its navigation names.

Usage: check_sprite.py <app repo, e.g. <bench>/apps/<app>> [--sprite <path>]

Exits 1 on an error; warnings are printed but do not fail.
"""

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET


def find_sprite(repo, app):
	path = os.path.join(repo, app, "public", "icons", "module-icons.svg")
	return path if os.path.exists(path) else None


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("repo")
	parser.add_argument("--sprite")
	args = parser.parse_args()

	repo = os.path.abspath(os.path.expanduser(args.repo))
	app = os.path.basename(repo)
	sprite = args.sprite or find_sprite(repo, app)
	errors, warnings = [], []
	if not sprite:
		sys.exit(f"no sprite at {app}/public/icons/module-icons.svg; create one with new_sprite.py")

	svg = open(sprite).read()
	try:
		ET.fromstring(svg)
	except ET.ParseError as e:
		warnings.append(f"not valid XML ({e}); the desk tolerates it, but a `--` inside an <!-- comment --> is the usual cause")

	ids = re.findall(r'<symbol\b[^>]*\bid="([^"]+)"', svg)
	prefix = app
	for symbol_id in ids:
		if not re.fullmatch(rf"icon-{prefix}-[a-z0-9-]+-duotone", symbol_id):
			errors.append(f"symbol id {symbol_id!r} must be icon-{prefix}-<name>-duotone")
	for tag in re.findall(r"<symbol\b[^>]*>", svg):
		if 'viewBox="0 0 24 24"' not in tag:
			errors.append(f"symbol without viewBox 0 0 24 24: {tag[:80]}")
	dupes = {i for i in ids if ids.count(i) > 1}
	if dupes:
		errors.append(f"duplicate symbol ids: {sorted(dupes)}")

	style = (re.search(r"<style>(.*?)</style>", svg, re.S) or [None, ""])[1]
	body = svg.split("</style>", 1)[-1]
	used = set(re.findall(rf'class="({prefix}-[\w-]+)"', body))
	styled = set(re.findall(rf"\.({prefix}-[\w-]+)", style))
	for cls in sorted(used - styled):
		errors.append(f"class {cls} is used but has no CSS")
	for cls in sorted(styled - used):
		warnings.append(f"CSS for .{cls} is not used by any symbol")
	for rule in re.findall(r"\{[^{}]*\banimation:[^{}]*\}", style):
		if "animation-play-state: var(--icon-motion, paused)" not in rule:
			errors.append(f"an animation is not held by --icon-motion: {' '.join(rule.split())[:90]}")
	for name in set(re.findall(r"@keyframes ([\w-]+)", style)):
		if not name.startswith(prefix + "-"):
			errors.append(f"@keyframes {name} must start with {prefix}-")
	for color in sorted(set(re.findall(r"#[0-9a-fA-F]{3,6}\b", body))):
		warnings.append(f"hard-coded colour {color} in a symbol; use the duotone variables")

	names = {i[len("icon-"):] for i in ids}
	referenced = {}
	for path in (glob.glob(f"{repo}/{app}/dock/*/*.json") + glob.glob(f"{repo}/{app}/*/sidebar/*/*.json")
			+ glob.glob(f"{repo}/{app}/*/workspace/*/*.json")):
		doc = json.load(open(path))
		for row in [doc, *doc.get("items", [])]:
			for key in ("icon", "header_icon"):
				if row.get(key):
					referenced.setdefault(row[key], set()).add(os.path.relpath(path, repo))
	for icon, paths in sorted(referenced.items()):
		if icon.startswith(prefix + "-") and icon not in names:
			errors.append(f"{icon} is used in {sorted(paths)} but not in the sprite")
		elif not icon.startswith(prefix + "-"):
			warnings.append(f"{icon} (not this app's) is used in {sorted(paths)}")
	unused = sorted(names - set(referenced))
	if unused:
		warnings.append(f"symbols not used by the dock, sidebars or workspaces: {unused}")

	hooks = open(os.path.join(repo, app, "hooks.py")).read()
	if not re.search(rf"^app_include_icons\s*=.*/assets/{app}/icons/module-icons\.svg", hooks, re.M):
		errors.append(f'hooks.py needs app_include_icons = ["/assets/{app}/icons/module-icons.svg"]')

	print(f"{sprite}: {len(ids)} symbols, {len(referenced)} icon names referenced")
	for w in warnings:
		print("  warning:", w)
	for e in errors:
		print("  ERROR:", e)
	sys.exit(1 if errors else 0)


if __name__ == "__main__":
	main()
