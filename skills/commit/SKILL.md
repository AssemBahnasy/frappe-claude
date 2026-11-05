---
name: commit
description: Commit finished, verified work in Frappe apps - one commit per app repo, conventional commit messages, pre-commit checks. Only when the user explicitly asks to commit (or push / open a PR).
argument-hint: "[app ...]"
disable-model-invocation: true
---

# Commit

Read first: `~/.claude/rules/frappe/git.md`.

1. Find what changed in every repo (`apps/` itself is not a repo):

   ```bash
   cd <bench>/apps
   for d in */.git; do r=${d%/.git}; s=$(git -C "$r" status --short); [ -n "$s" ] && echo "== $r" && echo "$s"; done
   ```

   `frappe` must have no changes; if it does, stop and tell the user.
2. For each app in scope: show the diff summary, run `pre-commit run --files <changed files>`
   inside the repo, fix what it reports.
3. If on `version-16`, ask whether to commit there or on a new branch (`feat/<topic>`).
4. Stage the files by name (never `git add -A` blindly), then commit with a conventional message:

   ```
   feat(trip): record proof of service photos

   <why, in one or two lines, if not obvious>
   ```

   End the message with the attribution lines the session asks for.
5. Push or open a PR (`gh pr create` against `version-16`) only if the user asked.
6. Report each repo, branch and commit hash.
