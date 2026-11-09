# Ledger and Knowledge-Base Protocol (Google Drive)

**Why this exists.** Each Claude session starts with an empty workspace. The ledger and the growing knowledge base must therefore live somewhere permanent. Blake chose Google Drive.

**Design.**
- Everything that changes lives in **Google Sheets**, because the Sheets tools can append and update cells. The Drive `update_file` tool changes only metadata, not content.
- Write-once notes live as **Markdown files**.

## Contents
1. Drive layout
2. Ledger columns and allowed values
3. Start of every session (resume)
4. Creating a new project ledger
5. Adding and updating rows
6. Knowledge-base growth (ingest-source format)
7. Failure handling and fallbacks
8. Rules that keep the ledger trustworthy

---

## 1. Drive layout

```
My Drive/
└── Medical Ethics Research/                     (folder)
    ├── MER Knowledge Index                      (Google Sheet: one row per saved source)
    ├── MER Ledger - <project-slug>              (Google Sheet: one per review project)
    └── knowledge/                               (folder)
        └── kb-<source-slug>                     (Google Doc note per source; Markdown-formatted text)
```

**Known IDs** (created and smoke-tested on 2026-11-09). Confirm them by search; Blake may move or rename things.

| Item | ID |
|---|---|
| Root folder "Medical Ethics Research" | `1MToRo-PBHiho7OweJ3cyzlG1rBvFZegy` |
| "knowledge" folder | `1YYnpFadJd4xOWr2aAgun9n1uLNdwcnrc` |
| "MER Knowledge Index" sheet | `1rAcp5pcl-Re8i-n66rqyXo8OASu0lA2j0RbrM_L-jzg` (first tab is named "Untitled"; ranges without a tab name work) |
| First KB note (FDA final guidance, July 2026) | `16SN25GrMjGav4Y9dZHYm2Od6zt7UBeJpd3HskvQZcFM` |

**Tested behavior (2026-11-09):**
- CSV text uploaded with conversion on becomes a Google Sheet.
- `append_values`, `get_values`, and `update_values` work with tab-less ranges.
- Notes uploaded as `text/plain` with conversion on become Google Docs, which `read_file_content` returns as text.
- Notes uploaded as `text/markdown` *without* conversion came back **empty** from `read_file_content`. `download_file_content` returned them only as base64. So save notes as Google Docs.

- Find things by searching: `title = 'Medical Ethics Research' and mimeType = 'application/vnd.google-apps.folder'`.
- Never assume IDs carry over. Always search at session start.
- Record the IDs you find in the first ledger LOG row of the session, so later steps in the same session don't repeat the search.

## 2. Ledger columns and allowed values

Header row, exactly, in this order (columns A–K):

| Col | Name | Allowed values / format |
|---|---|---|
| A | ID | `Q-001` question, `T-001` task, `F-001` finding, `S-001` source, `D-001` decision, `R-001` risk, `L-001` log, `SC-001` scope item |
| B | Type | SCOPE, QUESTION, TASK, FINDING, SOURCE, DECISION, RISK, LOG |
| C | Item | One plain-English sentence. Active voice. |
| D | Status | OPEN, IN PROGRESS, ANSWERED, DISPUTED, BLOCKED, DONE, SUPERSEDED |
| E | Owner | MANAGER, GATHERER, STATISTICIAN, ETHICIST, CHECKER, BLAKE |
| F | Evidence label | VERIFIED FACT, SOURCE CLAIM, ANALYTICAL JUDGMENT, or blank (for tasks and logs) |
| G | Source | URL, DOI, NCT number, or "risk_calc.py: <command>" |
| H | Source tag | V, S, M, U (meanings as in fda-pipeline.md) |
| I | Checked on | YYYY-MM-DD |
| J | Links / notes | Related IDs (e.g., "answers Q-003; contradicts F-007"), short notes |
| K | Updated | YYYY-MM-DD HH:MM (America/New_York) |

**Why these columns.** A later session must answer four questions without re-reading anything:
1. What was asked?
2. What is known, and how sure are we?
3. Where did it come from?
4. What is still open?

## 3. Start of every session (resume)

1. **Find the folder and the ledger.** Search `title contains 'MER Ledger'` with `orderBy: modifiedTime desc`.
   - If several ledgers exist and the user didn't name the project, list them and ask which one.
2. **Read the whole ledger.** Use `get_values` with range `A:K`. Omitting the tab name reads the first tab.
3. **Summarize the state for the user** in under 10 lines:
   - open questions;
   - disputed findings;
   - blocked items;
   - the last LOG entry;
   - any FINDING whose "Checked on" is more than 60 days old *and* concerns pipeline or regulatory status. Mark these "re-verify before use."
4. **Append a LOG row:** "Session resumed; objective: …".

## 4. Creating a new project ledger

1. **Find or create the root folder** "Medical Ethics Research".
   - Use `create_file` with `title` and `contentMimeType: application/vnd.google-apps.folder`. If the connector rejects this, use the documented folder mimeType parameter it accepts.
2. **Create the ledger as a Google Sheet** by uploading CSV text:
   - `create_file` with:
     - `title: "MER Ledger - <project-slug>"`;
     - `parentId: <root folder id>`;
     - `contentMimeType: "text/csv"`;
     - `textContent:` the header row plus the initial SCOPE and QUESTION rows.
   - Leave conversion on (the default), so Drive converts the CSV to a Google Sheet.
   - Quote any field that contains a comma: `"text, with comma"`. Double any embedded quotes.
3. **Confirm the file is a spreadsheet** (mimeType `application/vnd.google-apps.spreadsheet`) and read it back with `get_values`.
4. **Template.** The header and starter rows are in `assets/ledger-template.csv`.

## 5. Adding and updating rows

- **Add:** `append_values` with:
  - `spreadsheetId: <id>`;
  - `range: "A:K"`;
  - `values: [[...11 cells...], ...]`.
  - Batch several rows in one call.
- **Update a status:**
  1. Read `A:A` with `get_values`.
  2. Find the row number of the ID.
  3. Write with `update_values`, for example range `D{row}:K{row}` for status through updated.
  4. Never update by guessing the row number.
- **Supersede rather than delete.** If a finding is wrong:
  1. Set its status to SUPERSEDED.
  2. Add a new FINDING row.
  3. Note "supersedes F-00x" in column J.
  - This preserves the audit trail.
- **When to write:**
  - at scope approval;
  - when a role reports;
  - when the checker reports;
  - at delivery;
  - at session end.
  - Write in small batches, not after every sentence.

## 6. Knowledge-base growth (ingest-source format)

This follows Blake's `ingest-source` skill: one pre-analyzed note per source, plus a one-line index entry, so a future session can use the source without re-reading the original.

1. **When to save a source.**
   - After research turns up a source worth keeping: a primary document, a key paper, or a regulatory action.
   - Don't save trivial or duplicate sources. Search the index first.
2. **Write the note** from `assets/kb-source-template.md`.
   - Include a summary, key concepts, key data (with page or table locations), notable short quotes (under 15 words each, at most one per source), relationships to other sources, and the verification tag and date.
   - Paraphrase. Never paste whole passages.
3. **Upload the note:**
   - `create_file` with:
     - `title: "kb-<slug>"`;
     - `parentId: <knowledge folder id>`;
     - `contentMimeType: "text/plain"`;
     - `textContent: <note>`.
   - Leave conversion on, so Drive stores the note as a Google Doc that `read_file_content` can read and Blake can open.
   - Notes are write-once. If a source changes (e.g., a trial posts results), create a new dated note and supersede the old row in the index.
4. **Append one row to "MER Knowledge Index"** (columns A–I):

   | Col | Name |
   |---|---|
   | A | Slug |
   | B | Title |
   | C | Type |
   | D | Date added |
   | E | Topics |
   | F | Drive file ID |
   | G | One-line summary |
   | H | Source tag |
   | I | Verified on |

5. **Read before researching.** At the start of research, search the index (`get_values A:I`) for relevant topics. Read matching notes with `read_file_content` before going to the web.

## 7. Failure handling and fallbacks

| Problem | What to do |
|---|---|
| Drive / Sheets tools not present in this session | Say so in one line. Keep the ledger as a local CSV with the same columns. Send it to Blake with SendUserFile at the end, and tell him it was not synced. The next session with Drive available imports it with `append_values`. |
| Connector returns an auth error | Suggest reconnecting the Google Drive connector. Continue with the local-CSV fallback. |
| CSV upload did not convert to a Sheet | Create an empty spreadsheet (`create_file` with `contentMimeType: application/vnd.google-apps.spreadsheet`, no content), then write the header with `update_values` range `A1:K1`. |
| Two ledgers with similar names | List both with modified dates and ask Blake. Never merge silently. |
| Write fails midway through a batch | Re-read the ledger, find what landed, and append only the missing rows. Don't duplicate. |
| Range or tab confusion | Use ranges without a tab name (first tab). If the sheet has several tabs, read metadata with `get_spreadsheet` first. |

## 8. Rules that keep the ledger trustworthy

0. **Keep it lean.**
   - Record questions, findings that bear on a conclusion, decisions, risks, and session logs. Don't record every sentence of the memo.
   - A Standard review should need about 25 rows or fewer.
   - The ledger exists so that a later session can resume. It is not a second copy of the memo.
1. **One fact per row.** One source per FINDING. If two sources agree, cite the stronger one and mention the other in column J.
2. **Every FINDING carries an evidence label, a source, a tag, and a check date.** No exceptions.
3. **Numbers come from `risk_calc.py`.** Record the command in column G.
4. **The CHECKER's verdicts are recorded as their own rows** (e.g., "F-004 confirmed against FDA CRL p. 3" or "F-006 DISPUTED: registry shows a different primary endpoint").
5. **Never mark a QUESTION ANSWERED** until every FINDING it depends on has passed the CHECKER or has been marked as a judgment.
