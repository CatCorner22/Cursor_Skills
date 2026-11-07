# Word mechanics for redlines and comments

Read this file in Redline and Comment modes, with the docx skill's own SKILL.md ("Editing existing documents", "Tracked changes", and "Comments"). SKILL.md's Redline steps say what to do; this file says how the markup works. `<docx-skill>` is the docx skill's folder (on claude.ai, usually `/mnt/skills/public/docx`).

## Tracked changes (Redline step 3)

- Work in `word/document.xml` after the docx skill's `merge_runs.py` has run.
- Put deleted words in `<w:del w:id="..." w:author="Blake's AI Agent" w:date="...">` with `<w:delText>`, and new words in `<w:ins ...>` with the same author.
- Change only the words that differ between the old and new text, and copy the run's own `<w:rPr>` into each new run, so a bold defined term next to a change keeps its bold.
- Give each change a `w:id` higher than every `w:id` already in any part of the file.
- Find each paragraph by its words; the lint's paragraph numbers count every paragraph in order, table cells included.
- Leave the other side's tracked changes alone: don't edit inside their `<w:ins>` or `<w:del>` (SKILL.md, Redline step 4).

## Validate the redline and make the clean copy (Redline steps 6 and 7)

1. Zip the folder, and check it: `python3 <docx-skill>/scripts/office/validate.py tracked.docx --original in.docx --author "Blake's AI Agent"` must report no untracked changes and no errors.
2. Make the clean copy from it: `python3 <docx-skill>/scripts/accept_changes.py tracked.docx clean.docx`. It accepts every tracked change, the other side's too; comments already in the file stay in it.
3. Validate the clean copy: `python3 <docx-skill>/scripts/office/validate.py clean.docx --original in.docx`, without `--author`. If it fails, run it again with `--auto-repair`; if it still fails, make the clean copy by hand: the same edits, without markup, on a fresh unzip of the original.
4. After you add comments to `tracked.docx` (step 7), validate it again with `--author "Blake's AI Agent"`.

## Comments (Comment mode)

- Add each comment with the docx skill's `scripts/comment.py`, passing `--author "Blake's AI Agent" --initials "BAR-AI"` (its defaults are "Claude" and "C"; never BAA).
- Place the markers it prints around the exact words of the finding in `word/document.xml`; a comment without markers doesn't show.
- For a line break inside 1 comment, pass `--raw` with `</w:t><w:br/><w:t xml:space="preserve">` between lines (a bare `<w:br/>` inside the text fails validation), and escape `&`, `<`, and `>` yourself.
- Validate the file afterward: `validate.py` with `--original in.docx`, and with `--author "Blake's AI Agent"` when the file is a redline.
