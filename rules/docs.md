# Docs

Each app keeps its docs at the repo root in `docs/` (`apps/<app>/docs/`). They are how
anyone, person or AI agent, learns the app: what it does, how it is built, and why. Start or
reorganise them with `/app-docs`, whose templates are in
`~/.claude/skills/app-docs/references/templates.md`.

## Layout

```
docs/
├── README.md                     the index: what the app does, a table of every doc
├── architecture/
│   ├── separation-of-concerns.md what the app owns / does not own, its layers, invariants
│   ├── contracts.md              its contracts with other apps: every Link, function and hook it uses of another app
│   ├── code-organization.md      the shared homes (utils/, public/js/utils/) and what each file holds
│   └── data-flow.md              how a record moves through the app and the suite
├── doctypes/README.md            every DocType: kind, naming, one line, link to its doc
├── <feature>/                    one folder per feature: README.md + one file per concern
├── api/                          one file per api/ module
├── setup/                        install, settings, roles and permissions
├── navigation/README.md          apps screen, dock, sidebars, icons
├── tests/README.md               where tests live and how to run them
└── translations.md               corrected Frappe translations
```

General rules live in `~/.claude/rules/frappe/`, a project's rules in its own `.claude/`; neither
in each app's `docs/`.

## Separation of concerns applies to docs (always, without being asked)

Any request to document something produces **short files, one concern each**, never one long
file. The user should never have to ask for this.

- **A topic is a folder.** Documenting "weighbridge tickets" means `docs/weighbridge-tickets/`
  with a `README.md` index and one file per concern (`fields.md`, `rules.md`, `status.md`,
  `form.md`, `permissions.md`, ...). A topic with a single concern may stay one file.
- **Size limit.** A file aims for under 60 lines and is split once it passes about 80. When an
  edit would push a file past that, split it in the same change.
- **`README.md` is only an index**: one or two sentences on the topic, then a table of its files
  (one line each). No content that belongs in a concern file.
- **Plan the split first.** Before writing, list the concerns and the file for each, and show
  that outline to the user with the docs.
- **One fact, one file.** Other files link to it instead of repeating it.
- Templates in `/app-docs` are per concern; when a template's sections grow, each section becomes
  its own file in the topic's folder.

## What a change updates

| Change | Docs to update |
|---|---|
| New or changed DocType | its doc in the feature folder (template "DocType"), `doctypes/README.md` |
| New business rule | the "Rules" table of the DocType or feature doc, with the function that enforces it |
| New shared helper | `architecture/code-organization.md` |
| New cross-app link or import | the contract table in `architecture/contracts.md`, and the project's agreed table of links, if it has one |
| New endpoint | `api/<concern>.md` |
| New setting, role or permission | `setup/` |
| New dock, sidebar, workspace or icon | `navigation/README.md` |
| New doc file | a row in its folder's `README.md` and in `docs/README.md` |

## How they are written

- File and folder names are lowercase with hyphens (`weighbridge-tickets.md`).
- Each file covers one concern (see above); it links to other files instead of repeating them.
- Facts are checked against the code and Frappe's source; each rule names the function or file
  that enforces it.
- Plain words and short sentences; tables for fields, rules, settings and options; small ASCII
  diagrams for flows and layers.
- Docs say what the code does now, not its history. Open design questions go in
  `docs/open-questions.md`, not in feature docs.
- Links are relative, so they work on GitHub and in an editor. After moving or renaming a file,
  check no link points to it.
- Written in English; user-facing labels are quoted as they appear in English.
