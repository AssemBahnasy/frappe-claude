---
name: app-docs
description: Start, extend or audit a Frappe app's docs/ folder - the index, architecture (separation of concerns, code organization, data flow), DocType and feature docs, api, setup, navigation and tests - from the templates, checked against the code. Use when an app has no docs yet, when a change needs its docs written, or when the user asks to document, write docs, explain the architecture, or check the docs are current.
argument-hint: "<app> [init | doctype <DocType> | feature <name> | audit]"
---

# App docs

Read first: `~/.claude/rules/frappe/docs.md` (layout, what a change updates) and
`architecture.md` (what separation-of-concerns docs must say). Templates:
[references/templates.md](references/templates.md).

**Always split by concern** (`rules/docs.md`, "Separation of concerns applies to docs"): a topic
is a folder with an index `README.md` and one short file per concern, under about 60 lines each.
Do this by default; the user should never need to ask.

## Plan before writing

For any topic, first list its concerns and the file for each, for example:

```
docs/collection-trips/
├── README.md        index
├── fields.md        the fields that matter
├── rules.md         validations and the functions enforcing them
├── status.md        the states and what moves a trip between them
├── form.md          what the form shows and does
└── permissions.md   who can read, create, submit
```

Include this outline in the reply, so the user sees the split.

## init: an app with no docs

1. Read the app: `hooks.py`, `modules.txt`, every DocType JSON (`find <app> -name '*.json' -path
   '*doctype*'`), `api/`, `utils/`, `public/js/`.
2. Create, from the templates: `docs/README.md`, `architecture/separation-of-concerns.md`,
   `architecture/contracts.md`, `architecture/code-organization.md`, `architecture/data-flow.md`, `doctypes/README.md`,
   `setup/README.md`, `tests/README.md`. Leave out folders the app has nothing for yet.
3. For a freshly scaffolded app, write only what is true now: the app's purpose (its
   `hooks.py` description), what it owns per the project's rules, and empty tables with their
   headers. No invented DocTypes.

## doctype / feature: docs for a change

1. Find which rows of "What a change updates" (`rules/docs.md`) the change touches.
2. Write or update each doc from its template; every rule names the function that enforces it
   (`validate_containers`, `utils/trips.close`).
3. Add new files to their folder's `README.md` and to `docs/README.md`.

## audit: are the docs current?

For the app (or the files a change touched), check and report:

- no file is longer than about 80 lines, and no `README.md` holds content beyond its index;
  split any that are:

  ```bash
  find <bench>/apps/<app>/docs -name '*.md' -exec wc -l {} + | awk '$1 > 80 && $2 != "total"'
  ```

- every DocType in the code has a row in `doctypes/README.md` and a doc; no doc describes a
  DocType, field or function that no longer exists (`grep` each named function);
- every `api/` module has an `api/` doc;
- every file in `utils/` and `public/js/utils/` has a row in `code-organization.md`;
- every Link or import to another app has a row in the contracts table, and matches the
  project's agreed table, if it has one;
- every relative link resolves:

  ```bash
  cd <bench>/apps/<app>/docs
  grep -rnoE '\]\(([^)#]+)' --include=*.md . | while IFS=: read -r f l m; do
    t="${m#](}"; case "$t" in http*) continue;; esac
    [ -e "$(dirname "$f")/$t" ] || echo "$f:$l broken -> $t"; done
  ```

Fix what is wrong, or list it for the user if fixing needs a decision. Docs ship uncommitted with
the change they describe.
