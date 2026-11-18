# UI

- **Mockups first.** Every UI decision (a new screen, widget, layout or restyle) is shown as a
  mockup and approved before any implementation code is written. Approved boards are referred to
  by number in the feature docs.
- Prefer the standard desk: a well-designed DocType form, list view, report and workspace come
  before a custom page. A custom page or Vue app needs a reason, and then follows `/frappe-vue`
  (classic page, form or dialog host; on 16.60+ an island page or a Vue Component field).
- Use Frappe's own components (`frappe.ui.Dialog`, `frappe.ui.Popover`, `frappe.ui.toast`,
  `frappe.ui.chart`, Frappe UI in Vue) before writing new ones. `frappe.utils.make_chart` and
  `frappe.Chart` are deprecated since 16.60.
- Status colours come from the DocType's states, never from a colour map in the view. Charts use
  the theme's palette.
- Every screen works in light and dark mode, and in each language the project ships, right to left included. Check them in the
  browser before calling a UI change done.
- Navigation (dock, sidebars, workspaces) follows `/app-navigation`; icons follow
  `/frappe-desk-icons`, one sprite per app, sharing one look across a suite.
