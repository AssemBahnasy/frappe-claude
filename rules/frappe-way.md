# Frappe's way

The rules come from Frappe's own apps (Frappe, ERPNext, HRMS, CRM, Helpdesk). When a rule here is
unclear, do what those apps do.

## Look up how Frappe does it now

Before building, creating or customising anything (a DocType, page, hook, report, desk UI,
build step), find how Frappe does it today. Never from memory. In this order (how:
`/frappe-source`):

1. **Frappe's official docs and wiki** (docs.frappe.io, github.com/frappe/frappe/wiki, and the
   docs inside the repo such as `hooks.md`, `ui/README.md`): what the feature is and how it is
   meant to be used.
2. **The Frappe app on the bench**, the code that will run. Check its version first (branch,
   `__version__`) and compare it with the latest official release: the bench can be behind the
   docs. Where they disagree, the bench decides what can be used here; say the bench is behind
   instead of using a feature it lacks.
3. **Official apps** (ERPNext, HRMS, CRM, Helpdesk, Insights, LMS, Builder, ...): how the Frappe
   team uses that mechanism. Use the bench copy, or GitHub at the branch matching the bench's
   Frappe when the app is not installed. Check each one's version and the Frappe range in its
   `pyproject.toml` (`[tool.bench.frappe-dependencies]`): an app built for an older Frappe shows
   an older way.

Say which sources you checked and at which versions, and cite them in the docs you write.
Official apps are read for patterns only: never import from or edit them, and respect their
licences (ERPNext and HRMS are GPL-3.0).

## The bench you are on

- Check which apps are there: `<bench>/sites/apps.txt`, `bench --site <site> list-apps`. Link to
  or import from an app only if this project requires it; a project's rules say what it may use.

## Reuse Frappe before writing code

| Need | Use |
|---|---|
| Background work | `frappe.enqueue` (long jobs), `scheduler_events` |
| Live updates | `frappe.publish_realtime` |
| Rate limits | `frappe.rate_limiter.rate_limit` |
| Naming | `autoname` / naming series / `naming_rule` in the DocType JSON |
| States and approvals | Workflow DocType, `is_submittable`, `docstatus` |
| Status colours | `get_indicator` / list view settings, from the DocType's states |
| Dialogs, toasts, charts | `frappe.ui.Dialog`, `frappe.ui.toast`, `frappe.ui.chart` (16.60+; `make_chart` before) |
| Vue in desk | `/frappe-vue`: classic hosts; on 16.60+ islands (Page type Frappe UI, Vue Component field) |
| Querying | `frappe.qb` or `frappe.get_list`/`get_all`; raw SQL only with a reason |
| Permissions | Role permissions in the DocType, `has_permission` / `permission_query_conditions` hooks |

## Global names

Anything that touches a global validation (a name that must be unique across the bench or the
site) is checked in Frappe's source before it is chosen, never assumed. Frappe rarely refuses a
clash; usually one side silently wins. Check a new name against the apps on the bench and the
site. Verified on v16.54, re-checked on 16.60.1:

| Name | Unique across | On a clash |
|---|---|---|
| Module (`modules.txt`, compared scrubbed) | The site, and the bench | Installing a second app with the module on the same site raises `DuplicateEntryError` (`installer.py: add_module_defs`); `--force` skips it and the row stays with the first app. Across a bench it only warns, and in bench commands the app read last takes the module, so the other's DocTypes resolve to the wrong folder (`__init__.py: setup_module_map`; requests, jobs and migrate map installed apps only). A site's custom module is renamed out of the way (`rename_conflicting_custom_module`) |
| DocType | The site | No error: each migrate deletes and replaces it with the other app's (`modules/import_file.py: import_doc`, `delete_old_doc`). Two apps may share a name on one bench, never on one site |
| Page, Report, Workspace, Sidebar, Print Format, other synced records | The site | No error: the same import, but the file with the newer `modified` replaces the other (`import_file_by_path`) |
| Role | The site | No error: the apps share it. A role a DocType names is created with `desk_access = 1` if missing (`doctype.py: make_module_and_roles`), so whichever app creates it first decides |
| `www/` page path | The site | No error: the app installed last wins (`website/page_renderers/template_page.py: set_template_path`) |
| `website_route_rules` route | The site | No error: Werkzeug picks one (`website/router.py: evaluate_dynamic_routes`); never rely on which |
| Bundle file name | The bench, across all its sites (`sites/assets/assets.json`) | No error: the later entry overwrites (`esbuild/esbuild.js: update_assets_obj`, `esbuild/assets_json.js`). Name them `<app>_<feature>.bundle.js` |
| Island name (16.60+) | The bench (`assets.json` key `<name>.island.js`) | Two builds writing one key fail the island build (`ui/vite/island/assets.js: writeIslandAssets`); two pages claiming one page-island name fail the page-island build (`ui/vite/island/pages.js`). Name them `<app>.<feature>` |

For any other global name, find where Frappe validates it and cite that function.

## Things v16 does differently

- Desk URLs are `/desk/<route>` (not `/app/`).
- Navigation is **Dock** (`<app>/dock/<app>/<app>.json`) + **Sidebar** + **Workspace**
  records synced from files (`frappe/model/sync.py`, `APP_ROOTED_DOCTYPES`). See `/app-navigation`.
- Tests use `frappe.tests.IntegrationTestCase` / `UnitTestCase` (`frappe/tests/classes/`).
- Hooks are listed in `apps/frappe/hooks.md`.

On an older bench, check these in its source; skills written for v16 say so in their text.
