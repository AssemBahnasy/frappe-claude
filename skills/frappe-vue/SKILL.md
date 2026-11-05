---
name: frappe-vue
description: Build Vue 3 UI inside the Frappe/ERPNext desk (v15/v16) — lazy-loaded bundle, controller class, Pinia store backed by a real DocType (the architecture Frappe core uses for its builders). Use when adding a visual builder/editor/canvas page, an interactive widget inside a DocType form, a Vue component inside a frappe.ui.Dialog, or when debugging/reviewing Vue code in a Frappe app (mount/unmount, bundle loading, store, styling). Not for standalone SPAs (frappe-ui portals) or website pages.
---

# Vue inside the Frappe desk

One architecture, two hosts. Verified on Frappe v16.54; its packages and the absence of the v17 Frappe UI page type re-checked on this bench (v16.55.1).

## Pick the host

| Need | Host |
|---|---|
| Visual builder, editor, canvas, multi-panel tool for one record | **Page** → [references/page-host.md](references/page-host.md) |
| Interactive widget inside a DocType form (preview, mini-editor, chart) | **Form** → [references/form-host.md](references/form-host.md) |
| Rich content inside a Frappe dialog | **Dialog** → [references/styling-and-dialogs.md](references/styling-and-dialogs.md) |
| Plain list/report/form behaviour | No Vue: use DocType, Report, form scripts |
| Customer-facing portal or mobile app | Not this skill: separate SPA |

Frappe v17 (`develop`) adds a third way, a Page of type **Frappe UI** drawn by a Vue island.
It is not in v16, so don't use it on v16 sites. To plan a move:
[references/frappe-ui-pages.md](references/frappe-ui-pages.md).

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
    `@vue-flow/core`, `vuedraggable`, `sortablejs`, `frappe-charts`. Add other
    libraries to the app-root `package.json`.
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
- [frappe-ui-pages.md](references/frappe-ui-pages.md): v17 `develop` only. Page type Frappe UI, the island contract, differences from the v16 page host, fit by page kind
