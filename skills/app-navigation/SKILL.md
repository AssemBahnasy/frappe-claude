---
name: app-navigation
description: Set up or change a Frappe app's place in the Frappe v16 desk - apps screen tile, dock buttons, sidebars and workspaces, stored as files the app ships. Use when the user asks for a workspace, sidebar, dock button, menu, home page, apps-screen tile, or "where users find" a DocType or report.
argument-hint: "<app>"
---

# Desk navigation (Frappe v16)

To see a working example, find an app that ships a dock: `find <bench>/apps -path '*/dock/*' -name '*.json'`.
Mockup the structure first (which dock buttons, which sidebar lists what) and get approval.

## Records and files

| Record | File in the app | Synced by |
|---|---|---|
| Apps screen tile | `hooks.py` → `add_to_apps_screen` (name, logo, title, route, `has_permission`) | hooks; `frappe/apps.py: get_apps` hides the tile when `has_permission` returns false |
| Dock | `<app>/dock/<app>/<app>.json` | `frappe/model/sync.py`, `APP_ROOTED_DOCTYPES` |
| Sidebar | `<app>/<module_folder>/sidebar/<name>/<name>.json` | `IMPORTABLE_DOCTYPES` |
| Workspace | `<app>/<module_folder>/workspace/<name>/<name>.json` | `IMPORTABLE_DOCTYPES` |
| Icons | `<app>/public/icons/module-icons.svg` + `app_include_icons` | `/frappe-desk-icons` |

- A sidebar is a shell: its name is the first part of the URL (`/desk/<sidebar>/<doctype>`), and
  each DocType opens in the one sidebar that lists it.
- Frappe gives a sidebar every workspace of its module, and the first sidebar of the module
  answers for them (`sidebar.py` `resolve_sidebar`). Put a Home workspace only on the module's
  first sidebar.
- A sidebar's title gives its URL, and sidebar and module names share those routes
  (`public/js/frappe/router.js`), so don't name a sidebar after another module.
- Pages (16.60+): a Page with **System Page** set opens with no sidebar and is left out of the
  module's sidebar items; one with **Shared Page** set opens in whichever sidebar is on screen
  (for pages that act on a document from anywhere, such as Print). A page cannot be both
  (`page.py: validate_shell`). Before 16.60 `system_page` did nothing, and many app pages carry
  `"system_page": 1`; on 16.60 they open in whichever sidebar came before. Keep it `0` on an
  app's pages (Frappe sets it only on Desktop, Setup Wizard, Profile, Search, Notifications;
  ERPNext on none): find them with `grep -rl '"system_page": 1' <app> --include=*.json`, set
  `0`, bump `modified`, migrate.
- A sidebar item linking a Page may carry a `route`: a relative path inside that page
  (`<page>/<route>`), no query or fragment (`sidebar.py: validate_item_route`). Two items linking
  one page are told apart by it.
- A module left out of the dock has no button on the rail.
- Recommended: each sidebar opens on a workspace of the same name, which repeats its top links
  as shortcuts and has one card per sidebar section.
- Use the tile's `has_permission` to hide it from Website Users, so they are never sent to the
  desk.
- The old `workspace_sidebar/` and `desktop_icon/` records are not used in v16 for this; use Dock
  and Sidebar.

## How to change them

1. Preferred: on `<site>` (developer mode) use the desk's sidebar editor and Manage Dock;
   they write the JSON back into the app.
2. Or edit the JSON and bump each file's `modified`, or migrate skips it.
3. `cd <bench> && bench --site <site> migrate && bench build --app <app>`, hard-refresh
   the desk, check in each language the project ships.
4. Document it in the app's `docs/navigation/README.md` (dock table, sidebars, files).

## Consistency across a suite

Each app gets its own apps-screen tile and dock. Keep labels parallel across apps
(Home, Setup, Reports) and take icons from one shared look.
