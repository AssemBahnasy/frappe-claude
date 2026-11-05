# Testing

- A change comes with tests for what it changes. A test checks behaviour, not the
  implementation.
- DocType tests sit beside the DocType (`test_<doctype>.py`, `IntegrationTestCase` from
  `frappe.tests`); cross-cutting tests go in `<app>/tests/`. Pure logic uses `UnitTestCase` and
  needs no site data.
- Tests create the records they need (helpers in `<app>/tests/utils.py` or test records) and do
  not depend on data someone entered on the site. No network, API keys or external services:
  patch them.
- Run from the bench root (the site needs `allow_tests`; set once with
  `bench --site <site> set-config allow_tests true`; if the project names a test site, tests run
  there, never on the development site):

  ```bash
  cd <bench>
  bench --site <site> run-tests --app <app>
  bench --site <site> run-tests --app <app> --doctype "<DocType>"
  bench --site <site> run-tests --app <app> --module <app>.tests.test_<x>
  ```

- Lint the changed files: `ruff check <files> && ruff format <files>`; `pre-commit run --files
  <files>` inside the app repo runs the same checks as CI.
- CI (`.github/workflows/ci.yml`) installs the app on a fresh site and runs its tests; it does
  not install other apps unless the workflow says so. When an app gains `required_apps`,
  update its CI to get those apps too.
