---
paths:
  - "**/*.js"
  - "**/*.vue"
---

# Form scripts and desk JavaScript

Written the way ERPNext and Frappe core write them:

- Comments are brief: two sentences at most, saying *why*, never a paragraph.
- Every handler and helper is a method inside `frappe.ui.form.on("DocType", {...})`. A field
  event calls `frm.trigger("...")`; helpers are called as `frm.events.helper(frm, ...)`.
- Per-form state lives on `frm`. No module-level functions, caches or mutable state.
- Server calls through `frm.call`, `frappe.call` or `frappe.db.get_value(...).then`; never
  `fetch` to `/api` by hand.
- Link filters with `frm.set_query`; buttons with `frm.add_custom_button(__("..."), ..., __("Group"))`.
- `__()` on every user-facing string; tabs, double quotes (prettier + eslint via pre-commit).
- List view settings in `<doctype>_list.js`; status colours come from the DocType's states.

Desk pages (`frappe.pages[...]`) may keep module-level helpers and classes, as Frappe's own pages
do.

## Bundles and Vue

Any Vue in the desk (builder page, widget in a form, Vue in a dialog) follows `/frappe-vue`
(`~/.claude/skills/frappe-vue/SKILL.md`): read it, and its `pitfalls.md`, before
writing or reviewing Vue code. In short:

- Bundles live in `<app>/public/js/` and are named `<app>_<feature>.bundle.js` (`assets.json` is
  keyed by bare filename across apps).
- The host loads them with `frappe.require` when the feature opens; only small launchers go in
  `app_include_js`.
- A plain JS class mounts the app (`createApp` → `SetVueGlobals` → its own Pinia → mount) and
  destroys it (`unmount` + `$dispose`) before every re-mount and on page hide.
- The DocType record is the source of truth; the store loads and saves it.
- Styling uses Frappe's CSS variables and logical properties (`inset-inline-start`,
  `padding-inline`), so dark mode and right to left work without extra code.
- Use the packages Frappe already bundles (`vue`, `pinia`, `@vueuse/core`, `@vue-flow/core`,
  `vuedraggable`, `sortablejs`) before adding one. Charts: `frappe.ui.chart`.
- After changing bundles: `bench build --app <app>`.
- On 16.60+ a read-only dashboard page or form summary can be an island instead (Page type
  Frappe UI, Vue Component field): `/frappe-vue` islands.md. Islands write through
  `frappe.xcall`, never a frappe-ui POST.

A checkbox grid for assigning many items, with reusable bundles ("profiles", like Role and Role
Profile), follows `/frappe-multiselect-checkbox-editor`.
