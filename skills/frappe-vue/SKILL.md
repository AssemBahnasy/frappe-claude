---
name: frappe-vue
description: Build Vue 3 UI inside the Frappe/ERPNext desk (v15/v16) — classic hosts (lazy-loaded bundle, controller class, Pinia store backed by a real DocType, as Frappe's builders do) and v16.60+ islands (Page type "Frappe UI", the "Vue Component" field, frappe.ui.mount_island, an app's islands/ frontend built with buildIslands, frappe.ui.chart). Use when adding a visual builder/editor/canvas page, a dashboard page, an interactive widget or read-only dashboard inside a DocType form, a Vue component inside a frappe.ui.Dialog, a chart in desk, or when debugging/reviewing Vue code in a Frappe app (mount/unmount, bundle loading, store, styling, islands). Not for standalone SPAs (frappe-ui portals) or website pages.
---

# Vue inside the Frappe desk

Two families. **Classic**: a bundle mounts Vue into desk's DOM (page, form or dialog host).
**Islands**: a Vue app with its own Vue and frappe-ui in a shadow root, mounted by desk. Verified
on Frappe 16.60.1; islands are absent on 16.56.0 and older, so check the bench first
([references/islands.md](references/islands.md)).

## Pick the host

| Need | Host |
|---|---|
| A new screen at its own route (16.60+): dashboard, directory, profile, chart, canvas tool, with its toolbar in frappe-ui | **Island page** (Page Type "Frappe UI") → [references/island-pages.md](references/island-pages.md) |
| A summary, dashboard or profile inside a form (16.60+); can be the same island as a page | **Vue Component field** → [references/island-fields.md](references/island-fields.md) |
| Builder built on desk controls and desk's page head (`make_control`, `page.add_field`, primary action), or any page before 16.60 | **Classic page** → [references/page-host.md](references/page-host.md) |
| Widget that edits the open record's fields through `frm.set_value` | **Classic form** → [references/form-host.md](references/form-host.md) |
| Rich content inside a Frappe dialog | **Classic dialog** → [references/styling-and-dialogs.md](references/styling-and-dialogs.md) |
| A chart anywhere in desk | `frappe.ui.chart(el, config)` ([references/islands.md](references/islands.md)) |
| Plain list/report/form behaviour | No Vue: use DocType, Report, form scripts |
| Customer-facing portal or mobile app | Not this skill: separate SPA |

The rules and architecture below are for the classic family. Islands follow
[references/islands.md](references/islands.md) and build with
[references/island-build.md](references/island-build.md).

## Architecture

```
host (Page controller or Form script)
  └─ frappe.require("{app}_{feature}.bundle.js")
       └─ new {app}.ui.{Feature}({ wrapper, page|frm, name })   ← plain JS class
            ├─ createApp(Root) → SetVueGlobals(app) → app.use(pinia) → mount
            ├─ host chrome ↔ store: method calls in, watch() out
            └─ destroy(): stop watchers → app.unmount() → store.$dispose()
store (Pinia setup store)
  └─ loads/saves a real DocType record via frappe.db.get_doc / frappe.client.save
     meaning → normal fields + child tables; visual layout → hidden JSON field
```

The JS loads only when the feature opens. The data stays a normal DocType
record, so validation, permissions, versions, workflow and REST keep working
unchanged. Only public Frappe APIs are used.

## Rules

1. **Load bundles with `frappe.require` from the host.** `bench build` compiles every
   `*.bundle.js` under `{app}/public/`. Nothing goes in `hooks.py`.
2. **Name bundles `{app}_{feature}.bundle.js`.** `assets.json` is keyed by bare
   filename across all apps.
3. **Call `SetVueGlobals(app)` right after `createApp`**, so `__()` and `frappe` work in templates.
4. **Destroy before every re-mount**, and on page `hide`: `app.unmount()` +
   `store.$dispose()`. Emptying the wrapper does not unmount.
5. **Guard async mounts with a render token.** `frappe.require(...).then` can resolve late.
6. **One Pinia per mount:** `createPinia()` in the class, `useStore(pinia)`.
7. **The record is the source of truth.** Edit a clone, save with
   `frappe.client.save`, apply the returned doc.
8. **Register `window`/`document` listeners only inside component or store scope**,
   so `destroy()` removes them. Save on Ctrl+S through `wrapper.save_action`.
9. **Style with `<style scoped>`, Frappe CSS variables and Bootstrap 4 classes.**
   Dark mode then works automatically.
10. **Use Frappe's bundled packages:** `vue`, `pinia`, `@vueuse/core`,
    `@vue-flow/core`, `vuedraggable`, `sortablejs`. Add other libraries to the app-root
    `package.json`. Draw charts with `frappe.ui.chart`; `frappe.Chart` and
    `frappe.utils.make_chart` are deprecated since 16.60.
11. **Permissions come from DocTypes, not the Page.** Page roles only decide who opens the
    page. Every endpoint checks its own access, tools show only when
    `frappe.perm.has_perm(...)` allows them, and property panels respect field permission
    levels. App-specific actions get a custom Permission Type.

## Build checklist

1. Pick the host. Pick the backing DocType; add a hidden `JSON` field if you need
   to persist layout or positions.
2. Create files from the templates: page-host.md or form-host.md, plus store.md.
3. Property panels: [references/controls.md](references/controls.md).
4. Backend endpoints, if any: [references/python-api.md](references/python-api.md).
   Permissions for endpoints, tools and fields: [references/permissions.md](references/permissions.md).
5. Run `bench build --app {app}` (or keep `bench watch` running), then hard-reload.
   A new Page also needs `bench --site <site> migrate`.
6. Verify in the browser: open → edit → save → reload → switch record → leave
   and come back. One Ctrl+S should give exactly one save. The page's sidebar and
   breadcrumb should stay correct throughout, with no extra code (page-host.md §5).
7. Check [references/pitfalls.md](references/pitfalls.md).

## Placeholders

| Placeholder | Meaning | Example |
|---|---|---|
| `{app}` | Python app name | `my_app` |
| `{module}` | module folder (scrubbed) | `my_module` |
| `{feature}` / `{Feature}` | snake_case / PascalCase feature name | `route_designer` / `RouteDesigner` |
| `{page-name}` | Page name, hyphenated (folder is `{feature}`) | `route-designer` |
| `{DocType}` | backing DocType | `Route Plan` |
| `{layout_field}` | hidden JSON field on it | `designer_data` |

## References

- [page-host.md](references/page-host.md): Page JSON, controller, bundle class, root component, sidebar/breadcrumb, entry points
- [form-host.md](references/form-host.md): widget in an HTML field, writing back through `frm.set_value`
- [store.md](references/store.md): Pinia store backed by the record (load/save/reset/dirty), layout JSON field, undo/redo, shortcuts
- [controls.md](references/controls.md): real Frappe controls inside Vue; property panels built from DocType meta
- [styling-and-dialogs.md](references/styling-and-dialogs.md): CSS variables, sizing, Vue inside `frappe.ui.Dialog`
- [python-api.md](references/python-api.md): whitelisting, permission-aware queries, calling from Vue
- [permissions.md](references/permissions.md): page roles vs DocType rights, endpoint checks, tool gating, custom Permission Types, field-level access
- [pitfalls.md](references/pitfalls.md): failure modes and their fixes
- [islands.md](references/islands.md): the island contract, `frappe.ui.mount_island`, `useHost`, rules that fail silently (CSRF, desk controls, RTL, hidden mounts)
- [island-pages.md](references/island-pages.md): Page type Frappe UI, scaffolded or app-built, what desk gives and does not
- [island-fields.md](references/island-fields.md): the Vue Component field, a page island reused in a form, its props, the event bridge to the form script
- [island-build.md](references/island-build.md): an app's `islands/` frontend, `buildIslands`, bench build and watch
