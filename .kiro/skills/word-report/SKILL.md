---
name: word-report
description: Gated editing of the team's Word technical report (.docx) through the office-word MCP server. Use when reading, writing, or restructuring the report, or before calling any office-word MCP tool.
---

# Word report edits

Every change to the report passes through a **gate**: propose, wait for an explicit yes, apply, verify. One gate per change.

## Setup (once per session)

1. Get the report's absolute path from the user if it is not already in context. Pass absolute paths to every tool.
2. Ask the user to close the document in Word before the first write: the server rewrites the file, and Word's autosave would overwrite or conflict with it.
3. Read the target section first (`get_document_outline`, then `get_document_text` or `find_text_in_document`) so proposals quote the real current text.
4. The first gate of the session also proposes a backup with `copy_document` to `<name>.backup-<YYYY-MM-DD>.docx` next to the original.

## The gate

A **write** is any office-word tool outside the read-only set (`list_*`, `get_*`, `find_text_in_document`). Read-only tools run freely; every write goes through the gate.

1. **Propose.** Show:
   - where: the heading path (e.g. `2. Acquisition des données > Sources retenues`) and the anchor paragraph;
   - what: the tool and operation (insert after, replace, delete, format);
   - the exact text, verbatim: current → proposed, plus the style (`Normal`, `Heading 2`…).
2. **Wait.** Only an explicit approval of *this* proposal counts ("oui", "ok", "go", "yes"). An approval given for an earlier change covers that change alone. When the user amends the proposal, show the final version and wait again.
3. **Apply** exactly the approved content, with the approved tool, and nothing else.
4. **Verify.** Re-read the affected section and show the result. When it differs from what was approved (lost style, wrong anchor, duplicated paragraph), report it and open a new gate for the fix.

For several changes at once, number them and collect approval per item (the user may answer "1 et 3 oui").

## Course rules for the report

Source: `enonce.txt` §2.2.2 and §3.1.

- **AI mention.** Text drafted by the agent must carry the course's AI-use mention in each section or subsection concerned. Include the mention in every proposal containing drafted text. Ask the user for the exact wording the first time and reuse it for the rest of the session.
- **Human-made visuals.** Schemas, diagrams, images and code extracts must be produced by the team. For these, propose only a placeholder line, and only when the user asks for one.
- **Length.** At most 15 pages, excluding title page, table of contents, lists of tables/figures, and appendices. Flag any proposal that adds more than half a page.
- **Structure.** Sections 1–7 are fixed by §3.1; place new content under the matching heading.
- **Facts.** Numbers come from the application or the repository (counts, volumes, measured times), quoted exactly.
- **CHANGELOG.** After a gate that revises an already-submitted section, remind the user that `CHANGELOG.md` must list the revised sections. The team writes that file itself.
