# Frappe's way

The rules come from Frappe's own apps (Frappe, ERPNext, HRMS, CRM, Helpdesk). When a rule here is
unclear, do what those apps do.

## The bench you are on

- Check the bench's Frappe version before relying on anything version-specific:
  `git -C <bench>/apps/frappe branch --show-current`. The benches differ.
- Check which apps are there: `<bench>/sites/apps.txt`, `bench --site <site> list-apps`. Link to
  or import from an app only if this project requires it; a project's rules say what it may use.
- Read other apps for *patterns*: reference copies of ERPNext, HRMS, CRM and earlier custom apps
  are in `~/frappe-bench/apps` (read only). Respect their licences: ERPNext and HRMS are GPL-3.0.

## Reuse Frappe before writing code

| Need | Use |
|---|---|
| Background work | `frappe.enqueue` (long jobs), `scheduler_events` |
| Live updates | `frappe.publish_realtime` |
| Rate limits | `frappe.rate_limiter.rate_limit` |
| Naming | `autoname` / naming series / `naming_rule` in the DocType JSON |
| States and approvals | Workflow DocType, `is_submittable`, `docstatus` |
| Status colours | `get_indicator` / list view settings, from the DocType's states |
| Dialogs, toasts, charts | `frappe.ui.Dialog`, `frappe.ui.toast`, `frappe.utils.make_chart` |
| Querying | `frappe.qb` or `frappe.get_list`/`get_all`; raw SQL only with a reason |
| Permissions | Role permissions in the DocType, `has_permission` / `permission_query_conditions` hooks |

## Global names

A DocType name is global on a site, and Frappe gives no error on a clash. On migrate, a second
app's DocType of the same name deletes and replaces the first (`frappe/modules/import_file.py:
import_doc`, `delete_old_doc`). Check a new name against the apps the site will run.

## Things v16 does differently

- Desk URLs are `/desk/<route>` (not `/app/`).
- Navigation is **Dock** (`<app>/dock/<app>/<app>.json`) + **Sidebar** + **Workspace**
  records synced from files (`frappe/model/sync.py`, `APP_ROOTED_DOCTYPES`). See `/app-navigation`.
- Tests use `frappe.tests.IntegrationTestCase` / `UnitTestCase` (`frappe/tests/classes/`).
- Hooks are listed in `apps/frappe/hooks.md`.

On an older bench, check these in its source; skills written for v16 say so in their text.
