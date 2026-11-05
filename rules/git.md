# Git

- Each app is its own repo (`apps/<app>/.git`); `apps/` itself is not a repo. Run git inside the
  app (`git -C <bench>/apps/<app> ...`). A change touching two apps is two commits, one
  per repo.
- The app's default branch (`version-16` on a v16 bench) is the base. Commit or push only when the user asks; before committing
  on `version-16`, ask whether to branch first.
- Conventional commits (Frappe's `commitlint`): `feat:`, `fix:`, `refactor:`, `docs:`, `test:`,
  `chore:`, with an optional scope (`feat(trip): add proof of service photo`). Subject in the
  imperative, under 72 characters.
- Run `pre-commit run --files <changed files>` before committing; do not bypass hooks.
- Never commit `__pycache__`, `node_modules`, `public/dist`, site files or secrets.
- Never edit, commit to or push `apps/frappe` (upstream core).
