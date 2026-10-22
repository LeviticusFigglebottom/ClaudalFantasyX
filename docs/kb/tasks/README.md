# Task Board

One Markdown file per task: `<milestone>/<id>-<slug>.md`. Summary: `python3 tools/taskboard.py` (add `--role`, `--milestone`, or `--check`).

```markdown
---
id: M1-CMB-01
title: CTB battle sandbox scene
role: combat            # lead|architect|combat|progression|narrative|cinematics|rendering|character|environment|ui|audio|qa
status: todo            # todo|doing|review|done|blocked
owner_session: ""       # who is working on it (session or worktree name)
depends_on: [M1-CMB-00]
milestone: M1
request-from: ""        # set when another role asked for this
---
## Goal
## Acceptance criteria
- [ ] ...
## Notes
## Review log
- YYYY-MM-DD <reviewer role>: verdict, notes
```

Rules: claim before starting (commit the claim alone). A different role reviews (SPEC §12.3). `doing` with no commit for more than 48h is flagged STALE.
