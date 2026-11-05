# Pitfalls

Each entry: symptom → cause (Frappe source location) → fix.

## Lifecycle

### 1. Page teardown hook
**Symptom:** teardown code never runs.
**Cause:** `frappe/public/js/frappe/views/pageview.js` triggers only `on_page_load`
(once), `on_page_show` and `refresh`.
**Fix:** tear down at the start of every `on_page_show` render, and on the
wrapper's jQuery `hide` event (`views/container.js → change_to()`). Check
`e.target === wrapper`.

### 2. Emptying the wrapper as teardown
**Symptom:** after re-opening, watchers fire twice and old stores keep reacting.
**Cause:** removing DOM does not unmount a Vue app.
**Fix:** `destroy()` = stop external watchers → `app.unmount()` → `store.$dispose()`.

### 3. Store effects after unmount
**Symptom:** watchers or listeners created inside a store keep running.
**Cause:** a Pinia setup store runs in Pinia's effect scope, not the component's.
**Fix:** `store.$dispose()` in `destroy()`. Register listeners once, never from an
action that runs repeatedly, such as `load()`.

### 4. Hidden pages stay in the DOM
**Symptom:** a builder's keyboard shortcuts fire on other desk pages.
**Cause:** the desk hides pages instead of removing them (`container.js`).
**Fix:** register `window`/`document` listeners inside component or store scope,
and destroy on `hide`.

### 5. Ctrl+S on a Page
**Symptom:** Ctrl+S does nothing on the page.
**Cause:** `frappe/ui/keyboard.js` → `frappe.app.trigger_primary_action()` (`desk.js`)
clicks the primary button only for dialogs and forms. For a Page it calls
`frappe.container.page.save_action()`.
**Fix:** in `on_page_load`: `wrapper.save_action = () => wrapper.{feature}?.store.save();`
Frappe calls it only for the visible page.

### 6. Async mount races
**Symptom:** two apps in one wrapper, or record A's view appearing on record B.
**Cause:** `frappe.require(...).then` resolves after the user has moved on.
**Fix:** render token, incremented in `teardown()` and checked inside `.then`.

## Forms

### 7. One form object per DocType
**Symptom:** widget state from one record shows on another.
**Cause:** one `frappe.ui.form.Form` and its DOM are reused for every record of a
DocType (`views/formview.js`).
**Fix:** store the instance on `frm` (`frm._{feature}`) and remount on `refresh`.

### 8. HTML field options
**Symptom:** the widget disappears after save or refresh.
**Cause:** `form/controls/html.js → refresh_input()` re-renders `df.options` into
the wrapper whenever options are non-empty.
**Fix:** leave the HTML field's options empty.

### 9. Saving the form's record from the widget
**Symptom:** `TimestampMismatchError`; the form shows stale values.
**Fix:** write through `frm.set_value` and let the form save.

## Loading and data

### 10. Loading a record
**Symptom:** "Loading..." forever when the user lacks permission or the record is gone.
**Cause:** `model/model.js → frappe.model.with_doc` resolves only on success.
**Fix:** `await frappe.db.get_doc(...)`. It rejects on failure and syncs `locals`.

### 11. Editing the object in `locals`
**Symptom:** unsaved edits appear in the form view of the same record.
**Fix:** edit a deep clone; after save, `frappe.model.sync(saved)` and re-clone.

### 12. Permission-blind queries
**Symptom:** users see records they have no permission for.
**Cause:** `frappe.get_all` = `get_list(..., ignore_permissions=True)` (`frappe/__init__.py`).
**Fix:** `frappe.get_list`, or `get_doc` + `check_permission`. See python-api.md.

## Build and assets

### 13. Bundle name collisions
**Symptom:** `frappe.require("x.bundle.js")` loads another app's file.
**Cause:** `sites/assets/assets.json` is keyed by bare filename for all apps.
**Fix:** `{app}_{feature}.bundle.js`.

### 14. Packages
**Cause:** esbuild resolves imports from every app's `node_modules`, including
frappe's (`esbuild/esbuild.js` NODE_PATHS). Frappe ships `vue`, `pinia`,
`@vueuse/core`, `@vue-flow/core`, `@vue-flow/background`, `vuedraggable`,
`sortablejs`, `@headlessui/vue`, `frappe-charts` and `frappe-datatable`.
**Fix:** import those directly. Add other packages to the **app-root**
`package.json`, then run `yarn` at the app root.

### 15. A Frappe-provided library is suddenly undefined
**Symptom:** after a Frappe upgrade, e.g. `L.map is not a function` / `L is not defined`.
**Cause:** libraries Frappe loads for its own UI can move from the global `libs.bundle.js`
to lazy bundles. Since v16.51 Leaflet is `leaflet.bundle.js` + `leaflet.bundle.css`
(its CSS is separate too, so a map without it renders broken).
**Fix:** load them with the feature, in parallel, the way core's Map view does:
`Promise.all([frappe.require("leaflet.bundle.js"), frappe.require("leaflet.bundle.css"), frappe.require("{app}_{feature}.bundle.js")])`.
Check `frappe/public/js/libs.bundle.js` before relying on any global.

**Load each asset set through one shared promise.** `frappe.require` marks a file loaded only
after it finishes (`frappe/public/js/frappe/assets.js → load_asset`), so two calls made close
together each add a `<script>` and the library **runs twice**. For Leaflet, the map then comes
from one copy and its layers from another, so lines and polygons fail with `reading 'x'`.
Frappe v16.51's Geolocation field calls `frappe.require` on every refresh, so refreshing it
while Leaflet is still loading (e.g. `frm.disable_form()` in `refresh`) runs Leaflet again. Cache the promise in the controller and reset
it in the dev `hot_update` callback (page-host.md §2). For a Geolocation field holding a line,
share its `load_lib()` the same way in the form's `setup` event.

### 16. Changes don't show up
**Fix:** `bench build --app {app}` (or `bench watch`), then a hard reload. A new
Page JSON needs `bench --site <site> migrate`.

## Styling

### 17. Global CSS from a component
**Symptom:** desk icons or Bootstrap components change look.
**Cause:** unscoped CSS and injected `<link>` stylesheets apply to the whole document.
**Fix:** `<style scoped>` + Frappe CSS variables + Bootstrap classes.

### 18. Accent colour variable
**Fix:** `var(--primary-color)`. There is no `--primary` in Frappe's SCSS.

## Permissions

### 19. Relying on Page roles to protect endpoints
**Symptom:** users without the page's roles can still call its Python methods.
**Cause:** roles are checked only when the page loads (`frappe/desk/desk_page.py`); a page
method call is a plain dotted command (`frappe/public/js/frappe/request.js`).
**Fix:** each endpoint checks access itself (permissions.md §1).

### 20. `frappe.model.can_create` on "User Cannot Create" DocTypes
**Symptom:** create tools never show, even for roles with Create.
**Cause:** `in_create` moves the DocType out of `frappe.boot.user.can_create`.
**Fix:** `frappe.perm.has_perm(doctype, 0, "create")`.

### 21. Edits that vanish on save
**Symptom:** a value edited in a property panel comes back unchanged, with no error.
**Cause:** the field is above the user's permission level, and the server resets it
(`Document.validate_higher_perm_levels`).
**Fix:** build panels with `frappe.perm.get_field_display_status` (permissions.md §4).

## Routing and chrome

### 22. Hardcoded desk URLs
**Cause:** v16 serves the desk at `/desk`, v15 at `/app`, and v16.51 rewrites page URLs to
`/desk/<workspace>/<page>` (`frappe.get_route()` still returns `["<page>"]`).
**Fix:** `frappe.set_route(...)`; `frappe.utils.get_form_link(...)` for links.

### 23. Sidebar workarounds on a Page
**Symptom:** the page stays blank with `set_active_workspace_item is not a function` in the
console, or the URL gains `?sidebar=…`.
**Cause:** v16.51 code re-pinned the sidebar in `on_page_show` and passed a `sidebar` route
option. v16.54 removed those sidebar methods and turns unread route options into query
parameters (`router.js`).
**Fix:** remove both. v16.54 picks the sidebar and keeps the breadcrumb by itself
(page-host.md §5).

### 24. Mounting Vue onto `.layout-main-section`
**Symptom:** `page.add_field()` fields never appear, or Frappe page chrome inside the main
section vanishes.
**Cause:** `page.main` (`.layout-main-section`) also holds Frappe's filter bar (`page.page_form`).
Emptying it, or mounting Vue onto it, removes that element, and later fields go to a detached node.
**Fix:** create a dedicated mount point once in `on_page_load`
(`wrapper.vue_host = $("<div>").appendTo(page.main)`) and mount there (page-host.md §2).

## Scoped CSS and desk events

### 25. `:global()` in scoped CSS
**Symptom:** in a right-to-left language the whole desk is mirrored, or a rule styles `<html>`.
**Cause:** Vue's scoped CSS compiles `:global([dir="rtl"]) .fi-chevron { … }` to `[dir=rtl] { … }`:
everything after `:global()` is dropped (checked in a built bundle on v16.54).
**Fix:** `.fi-chevron:dir(rtl) { … }`, which stays scoped; or an unscoped `<style>` block with a
prefixed class.

### 26. `frappe.router.off` never removes a handler
**Symptom:** a `frappe.router.on("change", …)` listener keeps firing after it was "removed".
**Cause:** `event_emitter.js` wraps the handler in `on()`, and `off()` unbinds a new wrapper,
which never matches.
**Fix:** `frappe.router.once("change", …)` guarded by a flag, or one long-lived handler.
