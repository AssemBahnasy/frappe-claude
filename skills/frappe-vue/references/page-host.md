# Page host — a full-page builder/editor for one record

Route: `/desk/{page-name}/<record name>` (v16; `/app/...` on v15 — always navigate
with `frappe.set_route`, never hardcode the prefix).

## Files

```
{app}/
├── {app}/{module}/page/{feature}/
│   ├── __init__.py
│   ├── {feature}.json          ← Page record (role-gated)
│   └── {feature}.js            ← page controller: lifecycle only
└── {app}/public/js/{feature}/
    ├── {app}_{feature}.bundle.js   ← controller class (the only entry point)
    ├── store.js                    ← Pinia store → store.md
    ├── {Feature}.vue               ← root component
    └── components/*.vue
```

Nothing is added to `hooks.py`.

## 1. Page record — `{feature}.json`

```json
{
 "doctype": "Page",
 "name": "{page-name}",
 "page_name": "{page-name}",
 "title": "{Feature Title}",
 "module": "{Module Name}",
 "standard": "Yes",
 "roles": [{ "role": "System Manager" }]
}
```

Created on `bench --site <site> migrate` (developer_mode needed only to create it
from the UI; files on disk sync either way). Roles gate who can open the page —
data permissions are still enforced server-side on every read/save.

## 2. Page controller — `{feature}.js`

Lifecycle only. No Vue, no business logic.

```javascript
const PAGE = "{page-name}";

// One shared load: concurrent frappe.require calls for the same file execute it twice.
let assets = null;
const load_assets = () => (assets ??= frappe.require("{app}_{feature}.bundle.js"));

frappe.pages[PAGE].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("{Feature Title}"),
		single_column: true,
	});
	// Mount point of its own: page.main also holds Frappe's filter bar (page.page_form).
	wrapper.vue_host = $("<div></div>").appendTo(page.main);

	// Ctrl+S on a custom Page calls frappe.container.page.save_action()
	// (desk.js → trigger_primary_action). Only forms and dialogs get the primary button clicked.
	wrapper.save_action = () => wrapper.{feature}?.store.save();

	// Frappe has no on_page_unload/on_page_hide hook. The desk container triggers a
	// jQuery "hide" event on the page wrapper when you navigate away — tear down there.
	// Check the target: "hide" events from child elements bubble up to the wrapper.
	$(wrapper).on("hide", (e) => {
		if (e.target === wrapper) teardown(wrapper);
	});

	// developer_mode: re-mount after `bench watch` rebuilds the bundle
	if (frappe.boot.developer_mode) {
		frappe.hot_update = frappe.hot_update || [];
		frappe.hot_update.push(() => {
			assets = null; // the rebuilt bundle has a new file name
			if (frappe.get_route()[0] === PAGE) render(wrapper);
		});
	}
};

// fires on every visit, including switching from record A to record B
frappe.pages[PAGE].on_page_show = function (wrapper) {
	render(wrapper);
};

function teardown(wrapper) {
	wrapper._render_token = (wrapper._render_token || 0) + 1; // cancels pending loads
	wrapper.{feature}?.destroy();
	wrapper.{feature} = null;
}

function render(wrapper) {
	teardown(wrapper);
	const token = wrapper._render_token;
	const name = frappe.get_route()[1];

	if (!name) return pick_record();

	load_assets().then(() => {
		if (token !== wrapper._render_token) return; // user moved on while loading
		wrapper.{feature} = new {app}.ui.{Feature}({
			wrapper: wrapper.vue_host,
			page: wrapper.page,
			name,
		});
	});
}

function pick_record() {
	const d = new frappe.ui.Dialog({
		title: __("Open {0}", [__("{DocType}")]),
		fields: [
			{
				fieldname: "name",
				fieldtype: "Link",
				options: "{DocType}",
				label: __("{DocType}"),
				reqd: 1,
				// get_query: () => ({ filters: { ... } }),
			},
		],
		primary_action_label: __("Open"),
		primary_action({ name }) {
			d.hide();
			frappe.set_route(PAGE, name);
		},
	});
	d.show();
}
```

The Link field already offers "Create a new {DocType}". If creation needs extra
inputs, add them to the dialog, then `frappe.db.insert({...})` followed by
`frappe.set_route(PAGE, doc.name)`.

## 3. Controller class — `{app}_{feature}.bundle.js`

Owns the Frappe page chrome (imperative) and boots Vue (reactive). The bridge is
**method calls in, `watch()` out** — nothing else.

```javascript
import { createApp, watch } from "vue";
import { createPinia } from "pinia";
import { use{Feature}Store } from "./store";
import {Feature}Root from "./{Feature}.vue";

class {Feature} {
	constructor({ wrapper, page, name }) {
		this.$wrapper = $(wrapper);
		this.page = page;
		this.name = name;

		// one app + one pinia per mount
		this.pinia = createPinia();
		this.app = createApp({Feature}Root);
		SetVueGlobals(this.app); // __() and frappe in templates
		this.app.use(this.pinia);
		this.store = use{Feature}Store(this.pinia); // pass pinia explicitly

		this.setup_page();
		this.app.mount(this.$wrapper.get(0));
		this.store.load(name);
	}

	setup_page() {
		const page = this.page;
		page.clear_actions();
		page.clear_menu();
		page.clear_custom_actions();
		page.clear_indicator();
		page.set_title(__("Editing {0}", [this.name]));

		// Ctrl+S is wired in the controller via wrapper.save_action. Don't bind your own.
		page.set_primary_action(__("Save"), () => this.store.save());
		const $reset = page.add_button(__("Reset Changes"), () => this.store.reset());
		page.add_menu_item(__("Open {0}", [__("{DocType}")]), () =>
			frappe.set_route("Form", "{DocType}", this.name)
		);

		// Vue → Frappe: reactive state drives the chrome
		this.stop_dirty_watch = watch(
			() => this.store.dirty,
			(dirty) => {
				if (dirty) page.set_indicator(__("Not Saved"), "orange");
				else page.clear_indicator();
				$reset.toggle(dirty);
			},
			{ immediate: true }
		);
	}

	destroy() {
		this.stop_dirty_watch?.(); // watch() outside a component is never auto-stopped
		this.app?.unmount(); // disposes component scopes + their listeners
		this.store?.$dispose(); // store scope is NOT disposed by unmount
		this.app = this.store = this.pinia = null;
	}
}

frappe.provide("{app}.ui");
{app}.ui.{Feature} = {Feature};
export default {Feature};
```

### Filters in Frappe's filter bar

For page-level filters, use Frappe's own bar under the page head (`page.add_field`), the way
core's Role Permissions Manager does. The class creates the fields, writes changes into the
store, and mirrors store changes back with `watch()`:

```javascript
const FILTERS = [
	{ fieldname: "status", fieldtype: "Select", label: __("Status"), options: "\nDraft\nActive" },
	{ fieldname: "region", fieldtype: "Link", options: "Region", label: __("Region") },
];

setup_filters() {
	this.remove_filters();
	const fields = FILTERS.map((df) => {
		const field = this.page.add_field({
			...df,
			...(df.fieldtype === "Link" && { only_select: 1 }), // no "Create a new …" in a filter
			change: () => this.store && (this.store.filters[df.fieldname] = field.get_value() || ""),
		});
		return field;
	});
	this.stop_filter_watch = watch(
		() => ({ ...this.store.filters }),
		(filters) => fields.forEach((field) => {
			const value = filters[field.df.fieldname];
			if ((field.get_value() || "") !== value) field.set_value(value);
		})
	);
}

remove_filters() { // call at the start of setup_filters() and in destroy()
	this.page.clear_fields(); // empties the bar only…
	this.page.hide_form();    // …so also hide it and drop the stale entries
	FILTERS.forEach((df) => delete this.page.fields_dict[df.fieldname]);
}
```

Select options taken from meta (`frappe.meta.get_docfield(...)`) need the DocType loaded first.
Add `frappe.model.with_doctype("{DocType}")` to the controller's shared load.

For a filter that takes several values, use `MultiSelectList`, as ERPNext report filters do (not
Table MultiSelect, which needs a child DocType). Its value is a list, so keep the store's empty value
`[]`, copy lists both ways, and compare with `frappe.utils.deep_equal` in the watch:

```javascript
{
	fieldname: "vehicle_type",
	fieldtype: "MultiSelectList",
	label: __("Vehicle Type"),
	get_data: (txt) => frappe.db.get_link_options("Vehicle Type", txt),
},

const value_of = (field) => {
	const value = field.get_value();
	return Array.isArray(value) ? [...value] : value || "";
};
// change:  this.store.filters[df.fieldname] = value_of(field)
// watch:   if (!frappe.utils.deep_equal(value_of(field), value))
//              field.set_value(Array.isArray(value) ? [...value] : value);
```

## 4. Root component — `{Feature}.vue`

```vue
<script setup>
import { use{Feature}Store } from "./store";
import Sidebar from "./components/Sidebar.vue";
import Canvas from "./components/Canvas.vue";

const store = use{Feature}Store(); // pinia is injected by app.use()
</script>

<template>
	<div class="{feature}-root">
		<div v-if="store.error" class="{feature}-state text-muted">{{ store.error }}</div>
		<div v-else-if="!store.doc" class="{feature}-state text-muted">{{ __("Loading...") }}</div>
		<template v-else>
			<aside class="{feature}-sidebar"><Sidebar /></aside>
			<main class="{feature}-canvas"><Canvas /></main>
		</template>
	</div>
</template>

<style scoped>
.{feature}-root {
	display: flex;
	gap: var(--margin-md);
	/* height: measured, see styling-and-dialogs.md "Full-height canvas" */
}
.{feature}-sidebar {
	width: 300px;
	flex-shrink: 0;
	overflow-y: auto;
	background: var(--fg-color);
	border: 1px solid var(--border-color);
	border-radius: var(--border-radius-lg);
}
.{feature}-canvas {
	flex: 1;
	overflow: auto;
	background: var(--fg-color);
	border: 1px solid var(--border-color);
	border-radius: var(--border-radius-lg);
}
.{feature}-state {
	margin: auto;
}
</style>
```

Children call `use{Feature}Store()` directly — no props-drilling, no provide/inject.
Keep components presentational; put load/save/mutation logic in the store.

## 5. Sidebar + breadcrumb (v16 desk)

Nothing to add. Checked in Frappe 16.60.1:

- **Sidebar:** the resolver reads a Page route's first segment as the entity, since every
  Page is in `frappe.boot.page_info` (`ui/sidebar/sidebar.js → entity_from_route`). So
  `{page-name}/<name>` opens in the Workspace Sidebar that lists the page (an item with
  `link_type: Page`, `link_to: {page-name}`) and stays there when the record changes.
  Two Page checkboxes change that (16.60): **System Page** opens with no sidebar, and
  **Shared Page** opens in whichever sidebar is on screen (`router.js: page_info_for`).
- **Breadcrumb:** the trail belongs to the page object (`ui/page.js → set_breadcrumbs`).
  Frappe sets it to the page title once, right after `on_page_load` (`views/pageview.js`),
  so it survives record switches.

For a different trail, call `wrapper.page.set_breadcrumbs([{ label }])` in `on_page_show`.
In `on_page_load` it is overwritten straight after.

Don't carry over v16.51 workarounds:

- **Re-pinning the sidebar** through `frappe.app.sidebar`: `set_active_workspace_item` is
  gone, so the call throws in `on_page_show`, before `render()`, and the page stays blank.
- **`frappe.route_options = { sidebar }` before `set_route`:** the router no longer reads
  it and appends it to the URL as `?sidebar=…` (`router.js`).
- **`frappe.breadcrumbs.add`:** compatibility layer, marked for removal in v17
  (`views/breadcrumbs.js`).

## 6. Entry points

Open the builder from the record:

```javascript
// {DocType} form script
frappe.ui.form.on("{DocType}", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Open {Feature Title}"), () => {
			frappe.set_route("{page-name}", frm.doc.name);
		});
	},
});
```

```javascript
// {DocType} list view — {doctype}_list.js
frappe.listview_settings["{DocType}"] = {
	button: {
		show: () => true,
		get_label: () => __("Design"),
		get_description: (doc) => __("Open {0} in {1}", [doc.name, __("{Feature Title}")]),
		action: (doc) => {
			frappe.set_route("{page-name}", doc.name);
		},
	},
};
```

## Behaviour you get

- JS downloads the first time the page opens, then is cached.
- Record A → record B: `on_page_show` fires → old app destroyed → fresh mount.
- Navigate away: `hide` → destroyed (unsaved edits are dropped).
  Navigate back: fresh mount + fresh fetch.
- Ctrl+S saves through `wrapper.save_action`, which Frappe calls only for the
  page currently shown. The "Not Saved" indicator follows `store.dirty`.
