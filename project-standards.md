# IPPSAnalytics Project Standards

This file defines how Claude should use Confluence content to audit and update each project repo.
Edit this file to change what gets checked or generated across all projects.

---

## README.md

Every project must have a `README.md` that contains the following sections in order:

1. **Title** — the project folder name as an H1 (e.g. `# 725-DIS-PaymentWorks_Metrics_Supplier_Set_Up`)
2. **Overview** — 2–3 sentence plain-English summary of what the project does and who it serves; pull from the Confluence "Business Need" or "Project Goal" section; skip template placeholder text
3. **Data Sources** — bullet list of input files or Oracle tables; pull from the Confluence "Data Source" section; skip blank placeholders; for each file-based source, include the exact filename as referenced in the code (e.g. `R-725-Custom_Field.csv`)
4. **Code Files** — bullet list of every file in the repo with a one-line description; infer the description from the file name convention:
   - `Q-*.sql` → Oracle query that extracts [what]
   - `S-*.ipynb` → Notebook that transforms/processes [what]
   - `P-*.sql` → Stored procedure for [what]
   - `main.ipynb` → Orchestration entry point
5. **Deliverables** — what the project produces (dashboard, report, CSV, FTP file, etc.) with any links from Confluence
6. **Links** — Confluence page URL; any JIRA ticket numbers mentioned in the Confluence page

Omit any section if there is genuinely no content for it (do not leave empty headers).

---

## File & Folder Checks

After generating the README, also check the following and report any issues:

- [ ] Every SQL file follows the `Q-[ID]-*.sql` / `P-[ID]-*.sql` naming convention
- [ ] Every notebook follows the `S-[ID]-*.ipynb` naming convention
- [ ] No extraneous files are present (e.g. `.DS_Store`, temp files, duplicate outputs)
- [ ] If a `main.ipynb` is referenced in Confluence but missing from the repo, flag it

---

## Code Comments

Apply these rules when adding or reviewing comments in SQL and notebook files:

**SQL files (`Q-*.sql`, `P-*.sql`):**
- Add a comment block at the top of every file with: project number, a one-line description of what the query does, and the key Oracle tables it touches
- Add inline comments above any non-obvious JOIN conditions, WHERE filters, or subqueries
- Do not comment self-explanatory column selections or standard boilerplate

**Jupyter notebooks (`S-*.ipynb`, `main.ipynb`):**
- The first cell should be a Markdown cell with: project number, notebook purpose, and inputs/outputs
- Each major logical section (load, transform, export) should be preceded by a Markdown cell with a short section header
- Add inline `#` comments only where the logic is non-obvious (e.g. a regex, a custom merge key, a workaround)
- Do not add comments that just restate what the code obviously does

---

## Scope of Changes

Only modify documentation and comments. Never edit actual code or logic. Specifically:

- **Allowed:** `README.md` content, SQL header comment blocks, inline `--` comments in SQL, Markdown cells in notebooks, inline `#` comments in notebook code cells
- **Not allowed:** SQL query logic, JOIN conditions, WHERE filters, SELECT columns, notebook data transformations, imports, file paths, or any line that affects what the code actually does

If code logic appears wrong or could be improved, flag it in the review summary for a human to decide — do not change it.

---

## Business Context File

`IPPSAnalytics-Setup/business-context.md` is a running data dictionary of Oracle field meanings, hardcoded values, business logic, and domain facts discovered across all project repos. Use it when writing inline comments — if a magic value or non-obvious filter already has an entry, reference it. If you encounter something new and meaningful during a review (a field meaning, a hardcoded ID, a business rule baked into a WHERE clause), add it to the file under the appropriate section.

Good candidates to add:
- Hardcoded IDs or codes whose meaning isn't obvious from the name (e.g. `PRC_BU_ID = '300000002352016'`)
- Business rules embedded in WHERE filters (e.g. exclusion lists, date thresholds)
- Oracle table or field meanings that aren't self-evident
- Cross-project dependencies (e.g. one project's output feeding another)
- System or integration facts (e.g. how BI Publisher exports are structured)

---

## Tone & Style

- Write in plain, professional English — not Confluence template language
- Be concise; avoid redundancy between sections
- Do not invent information not present in Confluence or the file list
- If a Confluence section is an unfilled template placeholder, skip it silently
