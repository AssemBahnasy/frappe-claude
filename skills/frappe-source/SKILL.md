---
name: frappe-source
description: How to find how Frappe does something now before building, creating or customising it - official docs and wiki, the bench's own Frappe source (after checking its version against the latest release), and official apps (ERPNext, HRMS, CRM, Helpdesk, Insights, LMS, Builder) on the bench or on GitHub at the matching branch. Use before using any hook, framework API, DocType option, desk UI or build mechanism you have not checked in this session, or when the user asks "how does Frappe do X", "is there a hook for", "where does Frappe".
argument-hint: "<mechanism>"
---

# Look up how Frappe does it now

The order and the reasons are in `rules/frappe-way.md` ("Look up how Frappe does it now").
This is how.

## 1. Official docs and wiki

| Source | Where |
|---|---|
| Framework docs | https://docs.frappe.io/framework |
| ERPNext, HR docs | https://docs.frappe.io/erpnext, https://docs.frappe.io/hr |
| Frappe wiki (migration guides, release notes) | https://github.com/frappe/frappe/wiki |
| Docs inside the repo | `apps/frappe/hooks.md`, `apps/frappe/ui/README.md` and `ui/island/decisions/`, a feature's own `README.md` |

Docs describe intent and can lag the code or run ahead of the bench. Note their version or
date when you use them.

## 2. The bench's version, against the latest release

```bash
cd <bench>/apps/frappe
git branch --show-current
grep -m1 __version__ frappe/__init__.py
git log -1 --format='%h %cd' --date=short
git ls-remote --tags --refs https://github.com/frappe/frappe 'v16.*' | sed 's#.*/##' | sort -V | tail -1
```

Same for an official app (`apps/<app>/<app>/__init__.py`). If the bench is behind, tell the user
which release adds what you need; never use a feature the bench lacks.

## 3. The bench's Frappe source

| Looking for | Where |
|---|---|
| A hook and what it does | `apps/frappe/hooks.md`, then `grep -rn "get_hooks(\"<hook>\"" frappe/` |
| DocType save/submit lifecycle | `frappe/model/document.py` (`run_method`, `_validate`, `insert`, `save`, `submit`) |
| DocType JSON options | `frappe/core/doctype/doctype/doctype.json`, `docfield/docfield.json` |
| File sync on migrate | `frappe/model/sync.py`, `frappe/modules/import_file.py` |
| Patches | `frappe/modules/patch_handler.py` |
| Permissions | `frappe/permissions.py`, `frappe/model/db_query.py` |
| Whitelisting, rate limits | `frappe/__init__.py` (`whitelist`), `frappe/rate_limiter.py` |
| Desk navigation (dock, sidebar, workspace) | `frappe/desk/doctype/{dock,sidebar,workspace}/`, `frappe/public/js/frappe/ui/sidebar/` |
| Pages, islands (16.60+) | `frappe/core/doctype/page/page.py`, `frappe/utils/island.py`, `frappe/public/js/frappe/ui/island/`, `ui/` |
| Form JS API (`frm.*`) | `frappe/public/js/frappe/form/form.js`, `script_manager.js` |
| CLI commands, build | `frappe/commands/*.py` (`@click.command`), `frappe/bundler.py`, `esbuild/` |
| Tests base classes | `frappe/tests/classes/` |
| Boilerplate for new files | `frappe/core/doctype/doctype/boilerplate/`, `frappe/utils/boilerplate.py` |

```bash
cd <bench>/apps/frappe
grep -rn "<name>" frappe --include=*.py | grep -v /tests/ | head
grep -rn "<name>" frappe/public/js | head
```

## 4. Official apps: how the Frappe team uses it

On the bench (`ls <bench>/apps`): read them in place, after checking their version (step 2).

Not on the bench: read them on GitHub, at the branch matching the bench's Frappe
(`version-16` if it exists, else `main` / `develop`):

```bash
git ls-remote --heads https://github.com/frappe/<app> | sed 's#.*refs/heads/##'
dir=$(mktemp -d) && git clone -q --depth 1 --branch <branch> https://github.com/frappe/<app> "$dir/<app>"
grep -A3 'frappe-dependencies' "$dir/<app>/pyproject.toml"   # the Frappe range it supports
```

Read the clone only: never install it, run its scripts or `yarn install` in it. For a few files,
`gh api repos/frappe/<app>/contents/<path>?ref=<branch>` avoids the clone.

Skip an app whose Frappe range does not include the bench's version, or say it shows an
older way. Never import from or edit official apps; respect their licences (ERPNext and HRMS
are GPL-3.0).

## 5. Record what you found

Say which sources you checked and at which versions. Cite the file and function in the docs
you write (`frappe/model/sync.py`, `APP_ROOTED_DOCTYPES`), so the next reader can check it too.
