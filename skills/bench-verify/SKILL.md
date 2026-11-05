---
name: bench-verify
description: Verify a change on a Frappe bench before calling it done - migrate, build, clear cache, lint, run the app's tests and check it in the browser. Use after any change to a Frappe app under <bench>/apps (DocType, hooks, Python, JS, translations), or when the user says "verify", "check it works", "run the tests", "migrate".
argument-hint: "<app> [doctype or test module]"
---

# Verify a change

Bench root `<bench>`, site `<site>` (tests on the project's test site if it has one), desk at
`http://<site>:<port>/desk`.
Run each step that applies, read its output, and report failures with the output. Never call a
step passed that was not run.

## 1. Lint the changed files

```bash
cd <bench>/apps/<app>
git status --short                      # what changed
ruff check <changed .py files> && ruff format <changed .py files>
pre-commit run --files <changed files>  # same checks as CI (eslint, prettier, json/yaml)
```

## 2. Apply to the site

| Changed | Run (from `<bench>`) |
|---|---|
| DocType / report / workspace / sidebar / dock JSON, patches, fixtures | `bench --site <site> migrate` |
| `hooks.py`, Python only | `bench --site <site> clear-cache` |
| JS, CSS, Vue, bundles, `locale/*.po` | `bench build --app <app>` |

`migrate` must finish without a traceback; a skipped JSON means its `modified` was not bumped.
`bench start` (Procfile) must be running for the browser and background jobs; if it is not, ask
the user to start it rather than starting it yourself.

## 3. Tests

```bash
cd <bench>
bench --site <site> run-tests --app <app>                       # all
bench --site <site> run-tests --app <app> --doctype "<DocType>"  # one DocType
bench --site <site> run-tests --app <app> --module <dotted.module>
```

If it refuses with "Testing is disabled", ask before running
`bench --site <site> set-config allow_tests true`.

## 4. Browser (when the change shows in the desk)

Open the form, list or page at `http://<site>:<port>/desk/...`, in each language the project
ships (`/desk/...?_lang=<lang>` or the user's language setting), light and dark. Use the browser skill
available in the session; if there is none, give the user the exact URLs and what to look for.

## 5. Report

One short table: step, command, result (pass / fail with the key error line). Then stop for
review.
