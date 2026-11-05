# Drawing a duotone desk icon

## The grid

- `viewBox="0 0 24 24"`, `stroke="none"`, `style="overflow: visible"` on every `<symbol>`.
- Keep the shape inside about 2–22 on both axes. The dock draws it at 24px, sidebars at 16px, so
  detail under ~1.2 units disappears.
- Prefer filled shapes. Strokes are for lines that are lines (a path, a handle, a check mark):
  width 1.4–2.4, `stroke-linecap: round; stroke-linejoin: round`.

## Two tones

Every shape takes one of two fills, never a hex colour:

| Tone | Use it for | Fill |
|---|---|---|
| light | the body: the big, calm shape that says *what* it is | `var(--duotone-light, var(--<p>-…))` |
| dark | the detail: what it *does*, and what usually moves | `var(--duotone-dark, var(--<p>-…))` |

Copy the exact `--<p>-…` fallback names from the sprite's `:root` block. They differ per app,
for example `--<app>-green`/`--<app>-ink` and `--<app>-green-light`/`--<app>-green-dark`. A stroke uses
`fill: none; stroke: var(--duotone-dark, …)`.

Aim for roughly 60–70% light area and 30–40% dark. An all-dark icon looks heavy in the dock,
and an all-light one vanishes on the active tile.

## Motion

Pick one movement that tells the story, such as a lid lifting, a bag dropping or a route being
walked. Take the block from [motions.md](motions.md) and rename the prefix.

Rules the checker enforces or that bite at runtime:

1. **Every animation is held**: `animation-play-state: var(--icon-motion, paused);`. Frappe's
   dock sets `--icon-motion: running` on hover. Only custom properties reach inside `<use>`.
2. **Keyframe `0%` is the resting pose.** A paused animation shows its first frame, so a shape
   that starts hidden or moved at 0% looks broken at rest.
3. **Origins**: `transform-box: view-box` + `transform-origin: 12px 7px` pivots on a grid point
   (hinges, gears, knots). `transform-box: fill-box` + `transform-origin: center` pivots on the
   shape itself (pops, line-writes from `left center`).
4. **Staggering** with `:nth-child(n)` counts siblings, so put the staggered shapes alone in
   their own `<g>`.
5. **Hover-only shapes** (rings, rays) use `opacity: var(--icon-motion-opacity, 0)`.
   Transitions (the door) use `calc(... * var(--icon-motion-opacity, 0))`.
6. Prefix every class and `@keyframes` name with the app (`<app>-lid`). The style block is a
   document stylesheet shared by every app's sprite.
7. Never put `--` inside an `<!-- comment -->`. It breaks XML, although the desk's HTML parser
   tolerates it.

## Reuse before drawing

Sprites already drawn in other apps are read-only references; copy symbols, never edit them there.
Find them with `find ~ -path '*/apps/*/public/icons/module-icons.svg' -not -path '*/node_modules/*'`.

Within a suite, check its other apps' sprites first, so they share one look.

To reuse one, copy the `<symbol>` and its motion block. Rename the id, the classes, the
`@keyframes` and the `--<app>-…` fallback variables to the target app's. A shared shape
recoloured by the target palette fits in, because the colours come from the variables.

## Checklist

- [ ] id `icon-<app>-<name>-duotone`, name in kebab-case, a noun for the concept
- [ ] only the two duotone fills, no hex
- [ ] reads at 40px in the preview at rest; mid-frames show the pivot where intended
- [ ] dark theme row still reads (the light tone is dark there and the detail is light)
- [ ] a one-line `<!-- Concept: what it shows. -->` comment above the symbol, like its neighbours
