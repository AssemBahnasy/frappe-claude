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

Anything that touches a global validation (a name that must be unique across the bench or the
site) is checked in Frappe's source before it is chosen, never assumed. Frappe rarely refuses a
clash; usually one side silently wins. Check a new name against the apps on the bench and the
site. Verified on v16.54:

| Name | Unique across | On a clash |
|---|---|---|
| Module (`modules.txt`, compared scrubbed) | The site, and the bench | Installing a second app with the module on the same site raises `DuplicateEntryError` (`installer.py: add_module_defs`); `--force` skips it and the row stays with the first app. Across a bench it only warns, and in bench commands the app read last takes the module, so the other's DocTypes resolve to the wrong folder (`__init__.py: setup_module_map`; requests, jobs and migrate map installed apps only). A site's custom module is renamed out of the way (`rename_conflicting_custom_module`) |
| DocType | The site | No error: each migrate deletes and replaces it with the other app's (`modules/import_file.py: import_doc`, `delete_old_doc`). Two apps may share a name on one bench, never on one site |
| Page, Report, Workspace, Sidebar, Print Format, other synced records | The site | No error: the same import, but the file with the newer `modified` replaces the other (`import_file_by_path`) |
| Role | The site | No error: the apps share it. A role a DocType names is created with `desk_access = 1` if missing (`doctype.py: make_module_and_roles`), so whichever app creates it first decides |
| `www/` page path | The site | No error: the app installed last wins (`website/page_renderers/template_page.py: set_template_path`) |
| `website_route_rules` route | The site | No error: Werkzeug picks one (`website/router.py: evaluate_dynamic_routes`); never rely on which |
| Bundle file name | The bench, across all its sites (`sites/assets/assets.json`) | No error: the later entry overwrites (`esbuild/esbuild.js: update_assets_obj`). Name them `<app>_<feature>.bundle.js` |

For any other global name, find where Frappe validates it and cite that function.

## Things v16 does differently

- Desk URLs are `/desk/<route>` (not `/app/`).
- Navigation is **Dock** (`<app>/dock/<app>/<app>.json`) + **Sidebar** + **Workspace**
  records synced from files (`frappe/model/sync.py`, `APP_ROOTED_DOCTYPES`). See `/app-navigation`.
- Tests use `frappe.tests.IntegrationTestCase` / `UnitTestCase` (`frappe/tests/classes/`).
- Hooks are listed in `apps/frappe/hooks.md`.

On an older bench, check these in its source; skills written for v16 say so in their text.
