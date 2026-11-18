# Frappe development: rules for every bench

**These apply only when the work is on a Frappe bench or app** (a folder with `sites/` and
`apps/frappe`, or an app inside one). On any other project, ignore this folder and the `/` recipes
listed here.

They live in the `frappe-claude` repo (`~/frappe-claude`, linked into `~/.claude/`). Edit them
there; commit only when asked.

## Placeholders

| Written here | Means |
|---|---|
| `<bench>` | The bench root: the folder holding `sites/` and `apps/`. Run `bench` from it |
| `<app>` | The app being worked on, its own git repo in `<bench>/apps/<app>` |
| `<site>` | The project's development site |
| `<port>` | The site's web port (`webserver_port` in `sites/common_site_config.json`) |
| `<lang>` | A language code the project ships (`ar`) |

## What a project states for itself

A project keeps its own facts in its own `CLAUDE.md` or `.claude/`, in a repo so they travel:
its bench, sites and test site, Frappe version and which other apps it may use, its apps and who
owns what, its languages and glossary, its licence, its status. **Read it first; where it differs
from these rules, the project wins.** If a project has none, ask for what the task needs.

## The rules that matter most

- **Frappe's way.** Follow the layout and style of Frappe, ERPNext, HRMS and CRM. Before any
  build, creation or customisation, look up how Frappe does it now: official docs, the bench's
  Frappe (check its version against the latest release), then official apps at a matching
  version, on the bench or on GitHub.
- **Propose, then build.** New DocTypes, cross-app links and screens are proposed (fields table,
  the form's layout, or mockup) and approved first.
- **Forms are designed.** Check how Frappe's apps lay out similar DocTypes; organise fields into
  tabs, sections and columns by logic, never one long column.
- **Right app, right direction.** Shared masters live in a suite's core app; apps link only in
  agreed directions, never in a cycle.
- **Separation of concerns and DRY.** UI → endpoints (`api/`, access and inputs only) →
  features (the business rules) → records (controllers, this record only); integrations alone
  talk to outside services. Shared code lives once in its home; second use moves it there. An
  app reads upstream records and writes only its own.
- **Docs ship with the change**, in the app's `docs/`, each rule naming the function that
  enforces it. A topic is a folder with an index `README.md` and one short file (under ~60 lines)
  per concern, never one long file.
- **Permissions come from Frappe**, checked on the server.
- **Strings are translated** (`_()`, `__()`, `locale/<lang>.po`).
- **One step at a time.** Build, verify, document, then stop for review. Tests and docs ship
  with the change. Commit only when asked.

## Rules (this folder)

| File | Covers | Loads |
|---|---|---|
| [workflow.md](workflow.md) | How work is done, when to stop and ask | always |
| [frappe-way.md](frappe-way.md) | Where to look up how Frappe does it now, the bench you are on, reusing Frappe, global names, v16 differences | always |
| [architecture.md](architecture.md) | Separation of concerns and DRY | always |
| [translations.md](translations.md) | `_()`/`__()`, `.po` files, right to left | always |
| [ui.md](ui.md) | Mockups first, desk components, dark mode, RTL | always |
| [testing.md](testing.md) | Tests, running them, lint, CI | always |
| [docs.md](docs.md) | Each app's `docs/` layout, what each change updates, style | always |
| [git.md](git.md) | Per-app repos, conventional commits | always |
| [python.md](python.md) | Python style and code layout | `*.py` |
| [form-scripts.md](form-scripts.md) | Form scripts, bundles, Vue | `*.js`, `*.vue` |
| [doctypes.md](doctypes.md) | DocType design, `modified`, naming, permissions | `doctype/`, `report/`, `workspace/`, `sidebar/`, `dock/` |
| [doctype-layout.md](doctype-layout.md) | Tabs, sections and columns of a DocType's form | `doctype/` |
| [api.md](api.md) | Whitelisted endpoints, `hooks.py` | `api/`, `hooks.py` |

## Recipes and agents

Skills, invoked as `/<name>`: `bench-verify`, `new-doctype`, `new-endpoint`, `new-report`,
`new-patch`, `seed-data`, `translations`, `app-navigation`, `frappe-vue`,
`frappe-multiselect-checkbox-editor`, `frappe-desk-icons`, `app-docs`, `frappe-source`, `commit`.
Agent: `frappe-reviewer`, to review uncommitted changes before asking the user for review.

## Keeping this current

A convention true for any Frappe app goes here. One true only for a project goes in that
project's own folder. A new recipe is a new `skills/<name>/SKILL.md` plus a name above, then run
`~/frappe-claude/install.sh`.
