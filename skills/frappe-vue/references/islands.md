# Islands — the contract

Frappe version-16 has **islands** (present on 16.60.1, absent on 16.56.0): a Vue app that carries its own Vue and
frappe-ui and draws inside a shadow root. Check the bench before using them:
`grep -c mount_island <bench>/apps/frappe/frappe/public/js/frappe/ui/island/loader.js`.

Sources: `apps/frappe/ui/README.md`, `ui/island/decisions/0001–0016`,
`frappe/utils/island.py`, `frappe/public/js/frappe/ui/island/loader.js`, `ui/island/mount.js`.

## Name, registry, mount

- An island is one ES module exporting `mount(el, context)`. Its **name is its key in
  `assets.json`** without `.island.js`. The build registers it; there is no hook.
- Names are one bench-wide namespace: `<app>.<name>`. A page island is `<app>.page.<page>`.
- `frappe.boot.ui_islands` lists the islands of the apps installed on the site
  (`island.py: get_ui_islands`).
- Desk mounts one with `frappe.ui.mount_island(name, el, props)`. The handle is synchronous:
  `update(props)`, `unmount()`, `ready` (a promise that rejects if the bundle is missing).
- `props` is Vue's props object: data keys plus `on*` listeners (`onTitle`, `onNavigate`).
  `update` merges into it.

## The entry

```js
import { mountVueIsland } from "@framework/ui/island";
import Root from "./Root.vue";

export const mount = (el, context) => mountVueIsland(el, { ...context, component: Root });
```

`mountVueIsland` opens the shadow root, adopts the app's one stylesheet, mirrors the desk
theme, gives frappe-ui overlays a portal inside the root, installs a memory router and calls
`SetVueGlobals`. Pass `configure: (app) => app.use(createPinia())` for plugins.

## Inside an island

- `__()`, `frappe.*` and desk dialogs (`frappe.ui.Dialog`, `frappe.confirm`) work: the dialogs
  render in `<body>`, outside the root. ERPNext's islands read `const __ = window.__`.
- `useHost()` (`@framework/ui/island`) gives `locale`, `timezone`, `user`, `theme`,
  `navigate(route)`, `format(value, df, doc)`, `developer_mode`. Navigate with
  `host.navigate`: a plain `<a>` inside the root reloads the page.
- Style with frappe-ui and Tailwind classes. Desk CSS does not cross the shadow boundary.

## Rules that fail silently

1. **Write with `frappe.xcall` / `frappe.call`, not a frappe-ui POST.** Desk keeps the CSRF
   token in `frappe.csrf_token` (`www/desk.html`); frappe-ui's `frappeRequest` sends it only
   from `window.csrf_token`. frappe-ui `useCall` / `createResource` are fine for GETs.
2. **No desk controls inside.** `frappe.ui.form.make_control`, `page.add_field` and
   controls.md render unstyled in the root. Use frappe-ui inputs or `@framework/ui` fields
   (`Link`, `FormLayout`, `Fields`).
3. **Right to left:** text direction inherits into the root, so logical classes (`ms-`,
   `text-start`) mirror. Tailwind `rtl:` variants do not match inside the root (it copies
   `data-theme`, not `dir`). Use logical properties, not `rtl:`.
4. **A hidden island stays mounted.** Page islands survive `hide`; a form island stays when
   the next record of the DocType opens. Guard `window` / `document` listeners and polling on
   visibility (ERPNext uses an `IntersectionObserver`).
5. **Apply the reka-ui patch** in the frontend's `postinstall` (island-build.md), or a popover
   opened over a dialog closes the dialog.

## Hosts

| Host | File |
|---|---|
| A Page of type Frappe UI | [island-pages.md](island-pages.md) |
| A Vue Component field in a form | [island-fields.md](island-fields.md) |
| Your own page, form or dialog: `frappe.ui.mount_island` | this file; lifecycle as in page-host.md |
| Building an app's islands | [island-build.md](island-build.md) |

Charts are an island too: draw with `frappe.ui.chart(el, config)` (frappe-ui chart config,
or a frappe-charts config it converts); `frappe.Chart` and `frappe.utils.make_chart` are
deprecated (decision 0016).
