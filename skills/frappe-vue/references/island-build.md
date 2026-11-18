# Building an app's islands

An app-built island (for a Vue Component field, an app-built island page, or
`frappe.ui.mount_island`) is compiled by the app's own frontend with `buildIslands`. The
pattern is ERPNext's `islands/` folder (ERPNext 16.60). Read [islands.md](islands.md) first.

Most apps don't need one: a scaffolded page island serves a page and a Vue Component field
with no frontend (island-pages.md, island-fields.md; HRMS has none). Build your own only for
packages outside Frappe's toolchain (Pinia, vue-konva, vis-timeline, vue-flow, d3), or to
share one bundle between many islands.

## Files

```
{app}/
├── package.json                  scripts call into islands/
└── islands/
    ├── package.json
    ├── build.js
    └── src/{feature}/index.js    the entry: mountVueIsland
        src/{feature}/{Feature}.vue
```

App root `package.json` (bench runs `yarn install` here, and `yarn build` from `bench build`,
`esbuild.js: run_build_command_for_apps`):

```json
{
	"scripts": {
		"postinstall": "cd islands && yarn install",
		"build": "cd islands && yarn build"
	}
}
```

`islands/package.json`: the toolchain is the app's own (decision 0005):

```json
{
	"private": true,
	"type": "module",
	"scripts": {
		"postinstall": "patch-package --patch-dir node_modules/@framework/ui/patches",
		"build": "node build.js --production",
		"dev": "node build.js --watch"
	},
	"dependencies": {
		"@framework/ui": "link:../../frappe/ui",
		"@vitejs/plugin-vue": "^6.0.0", "autoprefixer": "^10.4.2", "frappe-ui": "1.1.0",
		"patch-package": "^8.0.0", "postcss": "^8.4.5", "tailwindcss": "^3.4.3",
		"typescript": "^5.8.3", "vite": "8.1.6", "vue": "^3.5.14", "vue-router": "^4.2.2"
	},
	"resolutions": { "reka-ui": "2.10.1" }
}
```

Copy the versions from `apps/erpnext/islands/package.json` on the bench, not from here.
The `reka-ui` resolution must match the patch file name in `apps/frappe/ui/patches/`.

`islands/build.js`:

```js
import { buildIslands } from "@framework/ui/vite/island";

await buildIslands({
	app: "{app}",
	root: import.meta.dirname,
	entries: { "{app}.{feature}": "src/{feature}/index.js" },
	production: process.argv.includes("--production"),
	watch: process.argv.includes("--watch"),
});
```

## What the build does

- One Vite build for all entries; shared chunks for Vue and frappe-ui.
- Output in `sites/assets/{app}/dist/island/`, keys `{app}.{feature}.island.js|css`.
- One stylesheet per app; Tailwind scans the modules in the bundle (no `content`).
- Warns over `budget` (default 2 MB JS + CSS per island); pin it after the first build.

## Running it

| Command | Builds app islands? |
|---|---|
| `bench build --app {app}` | yes, through the root `build` script |
| `bench watch` | **no**; run `cd apps/{app}/islands && yarn dev` beside it |
| `bench setup requirements --node` | installs, through `postinstall` |

A watch rebuild does not hot-reload yet: refresh the page.

Commit `islands/yarn.lock`; never commit `node_modules` or `sites/assets`. CI that builds
assets needs the frappe checkout beside the app (the `link:` path).
