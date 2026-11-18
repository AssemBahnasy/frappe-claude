# Island pages — a Page of type Frappe UI

The Page DocType has a **Type** field (16.60+): empty is a classic page, `Frappe UI` makes desk
build the page, mount the island and set the head from what it reports
(`views/pageview.js: setup_island_page`). Read [islands.md](islands.md) first.

## Two modes

| Mode | `island` field | Built by | May import |
|---|---|---|---|
| Scaffolded | empty | Frappe: one Vite build for every Frappe UI page on the bench (`island-toolchain/`, from `after_app_build`) | `vue`, `frappe-ui`, `@framework/ui`, `@vueuse/core`, `leaflet`, `echarts`, any file of any page folder on the bench. **No Pinia, no app packages** |
| App-built | `<app>.<name>` | the app's frontend ([island-build.md](island-build.md)) | anything in the frontend's `package.json` |

Prefer scaffolded; HRMS ships both its Frappe UI pages that way. A scaffolded page must be
Standard. Saving it writes the entry and the `.vue`, once (`page.py: write_island_boilerplate`).
The folder then grows like HRMS's `hr/page/organizational_chart/`:

```
{app}/{module}/page/{feature}/
├── {feature}.json          "type": "Frappe UI"
├── {feature}.island.js     the entry, generated
├── {feature}.vue           the page
├── components/*.vue        its parts
├── utils.js                helpers (read `window.__`, `window.frappe`)
├── {feature}.py            the page's whitelisted API: API = "{app}.{module}.page.{feature}.{feature}"
└── test_{feature}.py       tests for that API
```

An app-built page needs no folder and need not be Standard; saving it checks the island is on
the site (`page.py: validate_island`).

## What the page gets

```vue
<script setup>
defineProps({ route: Array, query: Object }); // URL segments below the page, URL params
const emit = defineEmits(["title", "actions"]);
emit("title", __("Fleet"));                    // breadcrumb + browser tab
emit("actions", []);                           // page menu rows: { label, onClick | href }
</script>
```

- `route` / `query` update in place on a route change; the island is not re-mounted
  (`/desk/employee-profile/<id>` reads the id from `route[0]`).
- An action is a **page menu row** (`set_island_chrome`); `href` opens a new tab.
- Leaving keeps it mounted; coming back shows it as left.
- Desk shows a skeleton, then "This page has not been built" when the bundle is missing.
- Sidebar and breadcrumb: as any Page (page-host.md §5); keep System Page off on app pages.

## Buttons, Save and Ctrl+S

Desk's head gives no primary button, indicator, inner buttons or filter fields. Draw them in
the island: a toolbar of frappe-ui `Button`, `Select`, `Combobox`, `TabButtons` (HRMS org chart:
Add Employee, search, Expand all, export). Desk's Ctrl+S still fires inside the island and calls
the visible page's `save_action` (`ui/keyboard.js`, `desk.js: trigger_primary_action`):

```js
onMounted(() => (frappe.pages["{page-name}"].save_action = save));
```

The page's `.js`, `.css`, `.html` and `page_js` hooks are not loaded (`page.py: load_assets`);
switching an existing page warns about its `.js`.

## Fit

| Page | Host |
|---|---|
| Dashboard, directory, profile, chart, canvas tool on frappe-ui | Scaffolded island page |
| Needs Pinia, vue-konva, vis-timeline, vue-flow or other npm packages | App-built island page, or keep the classic page |
| Built on desk controls (`make_control`, `page.add_field`) and you won't rewrite them | Classic page (page-host.md) |

## Build and check

`bench build` (scaffolded pages build after every app build; a failure only warns and leaves
**every** page island on the bench unbuilt). `bench watch` rebuilds and re-mounts in place.
Then open `/desk/{page-name}` in light, dark and each language.

Examples: HRMS `hr/page/organizational_chart`, `hr/page/employee_profile`; Frappe
`desk/page/profile`, `search`, `notifications`.
