#!/usr/bin/env python3
"""Render a duotone sprite to a PNG sheet: light at rest, two animation frames, dark at rest, dark active.

Usage: preview.py <sprite.svg> <out.png> [--only name,name] [--size 40]

Symbols are inlined (not <use>d) so each frame can be sampled with a negative animation-delay.
Read the PNG afterwards to judge the drawing; mid-frames show whether transform origins are right.
"""

import argparse
import os
import re
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("sprite")
parser.add_argument("out")
parser.add_argument("--only", help="comma-separated symbol names (without icon-<app>- and -duotone)")
parser.add_argument("--size", type=int, default=40)
args = parser.parse_args()

svg = open(args.sprite).read()
style = re.search(r"<style>(.*?)</style>", svg, re.S).group(1)
light, dark = re.findall(r"--duotone-(?:light|dark): var\((--[\w-]+)\)", svg)[:2]
symbols = re.findall(r'<symbol[^>]*id="icon-[a-z0-9_]+-([\w-]+)-duotone"[^>]*>(.*?)</symbol>', svg, re.S)
if args.only:
	wanted = args.only.split(",")
	symbols = [s for s in symbols if s[0] in wanted]

size, pad = args.size, max(8, args.size // 5)
cell = size + 2 * pad + 26
per_row = max(1, 1240 // cell)
cells = "".join(
	f'<div class="c"><svg viewBox="0 0 24 24" style="overflow:visible">{body}</svg><span>{name}</span></div>'
	for name, body in symbols
)
rows = [("light · rest", "light", ""), ("light · 0.35s", "light", "t1"), ("light · 0.8s", "light", "t2"),
	("dark · rest", "dark", ""), ("dark · active", "dark", "act")]
html = f"""<!doctype html><html><head><style>{style}
body{{margin:0;font:11px sans-serif}} .row{{display:flex;flex-wrap:wrap;gap:6px;padding:10px}}
.light{{color-scheme:light;background:#f3f3f3}} .dark{{color-scheme:dark;background:#232323;color:#ddd}}
.c{{width:{cell}px;display:flex;flex-direction:column;align-items:center;gap:3px}}
.c svg{{width:{size}px;height:{size}px;padding:{pad}px;border-radius:12px;--duotone-light:var({light});--duotone-dark:var({dark})}}
.light .c svg{{background:#e6e6e6}} .dark .c svg{{background:#333}}
.act .c svg{{--duotone-light:var({light}-active);--duotone-dark:var({dark}-active)}}
.light.act .c svg{{background:#d6d6d6}} .dark.act .c svg{{background:#3d3d3d}}
.t1 svg,.t2 svg{{--icon-motion:running;--icon-motion-opacity:1}}
.t1 svg *{{animation-delay:-0.35s!important}} .t2 svg *{{animation-delay:-0.8s!important}}
h4{{margin:0;padding:6px 10px 0;font-size:11px}}</style></head><body>"""
html += "".join(f'<div class="{t} {c}"><h4>{label}</h4><div class="row">{cells}</div></div>' for label, t, c in rows)
html += "</body></html>"

lines = -(-len(symbols) // per_row)
height = len(rows) * (24 + lines * (size + 2 * pad + 22) + 10)
chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser") if shutil.which(c)), None)
with tempfile.TemporaryDirectory() as tmp:
	page = os.path.join(tmp, "preview.html")
	open(page, "w").write(html)
	if not chrome:
		shutil.copy(page, os.path.splitext(args.out)[0] + ".html")
		raise SystemExit("no Chrome found; wrote the HTML next to the PNG path instead")
	subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
		f"--window-size=1280,{height}", f"--screenshot={os.path.abspath(args.out)}", f"file://{page}"],
		check=True, capture_output=True)
print(f"{args.out}: {len(symbols)} symbols")
