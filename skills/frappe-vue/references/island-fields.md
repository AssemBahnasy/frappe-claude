# Island fields — the Vue Component field

A DocField of type **Vue Component** mounts an island in the form. `options` is the island
name; the form builder offers `frappe.boot.ui_islands`. Read [islands.md](islands.md) first.

The island can be either kind:

- **A page island, `<app>.page.<page>`: no frontend needed.** One `.vue` serves the page and
  the form, and branches on its props: `props.doctype` is set in the form, `props.route` on the
  page. HRMS: the Employee form's Profile tab is `hrms.page.employee-profile`
  (`hrms/hr/page/employee_profile/`, field in `hrms/setup.py`).
- **An app-built island**: ERPNext's Project form, Overview and Costing tabs
  (`overview_dashboard` / `costing_dashboard`, `erpnext/islands/`).

On another app's DocType the field is a Custom Field (`create_custom_fields` from `setup.py`
or a patch, `ignore_validate=True`), as HRMS adds it to Employee.

## What the island gets

`form/controls/vue_component.js: get_props`:

| Prop | Value |
|---|---|
| `doctype`, `name` | the record; `name` is `null` while new |
| `doc` | a **deep copy** of `frm.doc` |
| `is_new` | `true` while unsaved |
| `read_only` | the field is not writable for this user |

Props are pushed again 300 ms after each change to the form, and on refresh. The island stays
mounted when the next record of the DocType opens, so key data on `name`.

## Rules

- **It stores no value and cannot write the form.** It is in `no_value_fields` and
  `display_fieldtypes`. Writes go one of two ways:
  - a whitelisted endpoint (`frappe.xcall`), then reload the form;
  - an event the form script handles, so desk's own dialogs and `frm.set_value` do the work:

    ```js
    // island
    el.value.dispatchEvent(new CustomEvent("costing-set-estimate", { bubbles: true, composed: true }));
    // form script, in setup (runs once per form, not per refresh)
    $(frm.wrapper).on("costing-set-estimate", () => frm.events.set_estimate(frm));
    ```

    `composed: true` lets the event leave the shadow root. Data rides in `detail`
    (`event.originalEvent.detail`).
- **Tell the island about server-side changes** from `refresh`:
  `frm.wrapper.dispatchEvent(new CustomEvent("<feature>-refresh", { bubbles: true, detail }))`,
  listened for on `document` inside the island.
- **Hide it on new records** with `depends_on: eval:!doc.__islocal` when it reads saved data.
- **Load when on screen.** The form mounts every Vue Component as it loads, whatever the tab;
  fetch when an `IntersectionObserver` sees the element (ERPNext `useOnScreenCall`).
- **Desk only.** The loader is in `desk.bundle.js`; web forms do not draw it.
- **The island must be built before the field is added.** Saving the DocType throws
  "Island … is not on this site" (`doctype.py: check_vue_component_options`); install,
  patches and fixtures skip the check.

## Fit

| Need | Use |
|---|---|
| Read-only summary, dashboard, preview of the record | Vue Component |
| Widget that edits the record's fields | form-host.md (HTML field, `frm.set_value`) |
