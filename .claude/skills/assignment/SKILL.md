---
name: assignment
description: Run the 4-agent assignment pipeline (brief, answers, natural voice rewrite, Word document) plus proofreading on files in assignments/inbox/. Use as /assignment <name>.
---

# Assignment pipeline

Argument: `<name>`, a short label for this assignment (used for work and output filenames).

## Steps
1. **Check inputs.** `assignments/inbox/` must contain the assignment (.pdf/.docx) and optionally a template (.docx). Create `assignments/work/<name>/`. Check `assignments/my-style/` for writing samples; if empty, warn the user that the voice step will be generic.
2. **brief-analyst** → `brief.md`. Show the user the summary, tasks, word limits and template map, and **pause for confirmation** or corrections.
3. **answer-writer** → `answers.md`. Report any `[STUDENT INPUT NEEDED]` items and ask the user for them; insert the user's answers.
4. **voice-editor** → `humanized.md`.
5. **doc-builder** → `assignments/output/<name>.docx`.
6. **proofreader** → fixes in the .docx and `proofread-report.md`. If it names a failing section, re-run the relevant agent and repeat 5-6 (max 2 loops).
7. **Final report** to the user: output path, word counts, open issues, and a reminder to read through and add personal examples before submitting. Do not claim an AI-detection score.

Launch each agent with the Agent tool using its `subagent_type`, passing `<name>` and the file paths. Run steps strictly in order.
