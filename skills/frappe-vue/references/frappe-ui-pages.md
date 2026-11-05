# Frappe UI pages — the v17 successor (develop only)

Frappe `develop` (17.0.0-dev) lets a Page's **Type** be `Frappe UI`. An *island* then draws the
page: a Vue app in a shadow root that brings its own Vue and frappe-ui. It is not in
`version-16` (checked on v16.54), and no backport PR existed on 2026-10-31. Keep building
v16 pages with page-host.md. This file is for planning the move.

Sources on `develop`: `ui/README.md`, `ui/island/decisions/` (0001–0016),
`frappe/core/doctype/page/page.py`, `frappe/public/js/frappe/views/pageview.js`. The core
pages `profile`, `search` and `notifications` (`frappe/desk/page/`) are working examples.

## The island contract

- An island is one ES module that exports `mount(el, context)`. Its name is its
  `<name>.island.js` / `<name>.island.css` key in `assets.json`. Names share one bench-wide
  namespace, so prefix them with the app (decision 0014).
- `mountVueIsland` (`@framework/ui/island`) opens the shadow root, adopts the stylesheet,
  mirrors the desk theme and calls `SetVueGlobals`, so `__()` and `frappe` still work.
- Desk mounts one with `frappe.ui.mount_island(name, el, props)`. A frappe-ui app mounts the
  same island with `<Island name="…">`. Both use one host loop (`ui/island/host.js`), which
  owns the load, the unmount and the late-load race.
- `useHost()` inside a component returns `locale`, `timezone`, `user`, `theme` and `navigate`.

## A Page of type Frappe UI

Desk builds the page and mounts the island. The page ships no `.js` controller: an existing
`<page>.js` stops running, and validation warns about it.

| Mode | `island` field | Who builds it | What it may import |
|---|---|---|---|
| Scaffolded | empty | Frappe, one Vite build for every such page on the bench (`island-toolchain/`, run after each app build) | `vue`, `frappe-ui`, `@framework/ui` only |
| App-built | `<app>.<name>` | the app's own frontend, with `buildIslands` from `@framework/ui/vite/island` | anything in the app's `package.json` |

A scaffolded page must be Standard. Saving it writes the starter once, beside its JSON:

```
{app}/{module}/page/{feature}/
├── {feature}.json          type: "Frappe UI"
├── {feature}.island.js     entry, generated
└── {feature}.vue           the page, yours to edit
```

Its island name is `<app>.page.<page name>`. Then `bench build`. `bench watch` re-mounts it
in place.

## What the page gets from desk

```vue
<script setup>
defineProps({ route: Array, query: Object }); // segments below the page, URL params
const emit = defineEmits(["title", "actions"]);
// emit("title", "…")                            → breadcrumb + browser tab
// emit("actions", [{ label, onClick } | { label, href }]) → page menu rows; href opens a new tab
</script>
```

- **Route changes** update `route` / `query` in place. There is no re-mount per record.
- **Leaving the page** keeps the island mounted while hidden, and coming back shows it as it
  was (`pageview.js → setup_island_page`).
- **Loading and errors:** desk shows a skeleton, then "This page has not been built" if the
  bundle is missing.
- **Data:** call `frappe.xcall` directly, as Profile does, or use frappe-ui's `createResource`
  with `resourceFetcher: frappeRequest`.
- **Sidebar and breadcrumb:** it is still a Page, so the v16.54 behaviour in page-host.md §5
  holds.

## Differences from the v16 page host

| | v16 page host (page-host.md) | Frappe UI page |
|---|---|---|
| Code to write | controller, bundle class, render token, teardown | the `.vue` file |
| Styling | Bootstrap classes + Frappe CSS variables | frappe-ui + Tailwind in a shadow root |
| Page head | primary action, indicator, buttons, filter bar, Ctrl+S via `save_action` | title + menu rows only |
| Leaving | destroyed on `hide` | stays mounted |
| Other packages | app-root `package.json`, esbuild | an app frontend + `buildIslands` |

Not verified yet, inferred from the shadow root and the head contract:

- Frappe controls (`frappe.ui.form.make_control`, page filter fields) will render unstyled
  inside the island. Use frappe-ui components and `@framework/ui` fields instead (controls.md
  does not carry over).
- Listeners on `window` / `document` keep firing on other desk pages, because the island is
  not unmounted on hide. Guard them on visibility.
- Leaflet's stylesheet must be adopted into the shadow root. `@framework/ui` lists `leaflet`
  as a dependency; whether it ships a map component is unchecked.

## Fit by page kind

| Page kind | Fit |
|---|---|
| Dashboards | Good: scaffolded page, frappe-ui charts (`frappe.ui.chart`) |
| Builders and editors | Poor for now: no Save action, dirty indicator or Ctrl+S in the contract; vue-konva needs an app frontend |
| Map workspaces | Open: Leaflet CSS in the shadow root, map component unchecked |

When v17 nears, port the dashboards first. Re-check the contract for a primary action before
porting a builder.
