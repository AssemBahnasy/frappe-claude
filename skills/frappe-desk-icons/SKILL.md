---
name: frappe-desk-icons
description: Create or change an app's animated dual-tone desk icons for Frappe v16's dock, sidebars and workspaces (the module-icons.svg sprite pattern used by naqel, butler, waqf and frappe_intelligence). Use when asked for a new icon ("add a workshop icon", "an icon for waste containers"), to replace stock or ERPNext icons in an app's dock or sidebar with custom ones, to recolour or animate desk icons, or to start a sprite for an app that has none. Not for the apps-screen tile, which stays the app's original logo file.
---

# Desk icons for a Frappe app

An app ships one sprite, `<app>/public/icons/module-icons.svg`, loaded by
`app_include_icons = ["/assets/<app>/icons/module-icons.svg"]` in `hooks.py`. Each icon is a
`<symbol id="icon-<app>-<name>-duotone">` in two tones taken from the app's logo, animated while
its dock button is hovered. The dock, sidebar items, sidebar headers and workspaces name it as
`<app>-<name>-duotone`.

Scripts are in `scripts/`, next to this file
(`~/.claude/skills/frappe-desk-icons/scripts/`); run them by that path.

## 1. Find the sprite

```bash
ls <bench>/apps/<app>/<app>/public/icons/module-icons.svg
```

- **It exists:** read its `<style>` header for the palette variable names (`--<app>-…`) and two
  or three symbols, so the new icon matches their weight.
- **It doesn't:** sample the logo's colours, then create one:

  ```bash
  convert <logo> -alpha off -colors 8 -format "%c" histogram:info:- | sort -rn | head
  python3 ~/.claude/skills/frappe-desk-icons/scripts/new_sprite.py <bench>/apps/<app> --body '#22b573' --detail '#111111' --brand "the logo's green"
  ```

  Add the `app_include_icons` line it prints to `hooks.py`.

## 2. Design

Decide what the icon shows and which **one** movement tells its story. For example, a workshop
could be a garage with a turning gear or a working wrench, and containers could be a skip
whose lid lifts. Before drawing, search the other sprites for something close and reuse it. See
the table in [references/drawing.md](references/drawing.md).

## 3. Draw

Add the `<symbol>` at the end of the sprite, before `</svg>`, with a one-line comment above it
like its neighbours. Follow [references/drawing.md](references/drawing.md): a 24 grid, the two
duotone fills only, the body light and the detail dark. If the movement is new to this sprite,
copy its block from [references/motions.md](references/motions.md) into the `<style>` and rename
the prefix.

## 4. Check and look

```bash
python3 ~/.claude/skills/frappe-desk-icons/scripts/check_sprite.py <bench>/apps/<app>
python3 ~/.claude/skills/frappe-desk-icons/scripts/preview.py <sprite> /tmp/preview.png --only workshop,skip --size 96
```

Read the PNG. The icon must read at rest, the two mid-animation rows must pivot where you
intended, and the dark rows must still read. Iterate until they do. Finish with a full sheet at
the default size, to see it next to its neighbours.

## 5. Use it

Set the icon where it belongs (`icon` on a dock row or sidebar item, `header_icon` on a sidebar,
`icon` on a workspace):

- on a developer-mode site, through the desk's sidebar editor or Manage Dock, which write back to
  the app's files; or
- by editing `<app>/dock/…`, `<module>/sidebar/…` and `<module>/workspace/…` JSON directly. Bump
  each file's `modified` past the site's value, or the migrate skips it.

Then:

```bash
bench --site <site> migrate && bench build --app <app>
python3 ~/.claude/skills/frappe-desk-icons/scripts/check_sprite.py <bench>/apps/<app>   # no "not in the sprite" errors
```

Hard-refresh the desk and hover the dock button.

## 6. Document

If the app has `docs/navigation/` (an app may keep docs at the repo root), add the icon to its icon table and regenerate the sheet:

```bash
python3 ~/.claude/skills/frappe-desk-icons/scripts/preview.py <sprite> <bench>/apps/<app>/docs/navigation/icons.png
```

Leave the work uncommitted unless the user says to commit.
