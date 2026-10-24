# Collaboration Rules

## Personal work must stay in its owner's area

- Sarah's personal notes, drafts, experiment runs, and results belong only in `workspaces/sarah/`.
- Julien's personal notes, drafts, experiment runs, and results belong only in `workspaces/julien/`.
- Do not create, edit, move, copy, or overwrite files in the other person's workspace unless that person explicitly asks for it.
- When Sarah asks Codex to change code, run experiments, or push work, use a `sarah/*` branch only. Code changes may touch shared source files in Sarah's branch, but do not push them to `main`, `feat/*`, or `julien/*`, and do not merge them unless Sarah explicitly asks. Keep Sarah's personal notes, run logs, and findings in `workspaces/sarah/`. Never modify Julien's personal workspace as part of Sarah's work. Apply the equivalent rule to Julien's requests.

## Branches and shared work

- Sarah's individual work should use branches named `sarah/*`; Julien's should use `julien/*`.
- Shared code, experiment design, and final deliverables belong in shared project files. Keep Sarah's proposed shared-code changes on her `sarah/*` branch until she explicitly requests a pull request or merge. Do not push Sarah's changes directly to a shared branch.
- Keep personal run logs and findings in the owner's workspace until that person chooses to share or merge them.

## Permission limitation

These are collaboration rules, not technical access controls. GitHub repository collaborators can read and modify every file and branch in this private repository; GitHub does not enforce per-folder permissions. If Sarah and Julien must be technically unable to access each other's materials, store those materials in separate private repositories with separate collaborator lists.
