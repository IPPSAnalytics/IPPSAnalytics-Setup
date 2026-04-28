# IPPSAnalytics Project Standards

This file defines how Claude should use Confluence content to audit and update each project repo.
Edit this file to change what gets checked or generated across all projects.

---

## README.md

Every project must have a `README.md` that contains the following sections in order:

1. **Title** — the project folder name as an H1 (e.g. `# 725-DIS-PaymentWorks_Metrics_Supplier_Set_Up`)
2. **Overview** — 2–3 sentence plain-English summary of what the project does and who it serves; pull from the Confluence "Business Need" or "Project Goal" section; skip template placeholder text
3. **Data Sources** — bullet list of input files or Oracle tables; pull from the Confluence "Data Source" section; skip blank placeholders
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

## Tone & Style

- Write in plain, professional English — not Confluence template language
- Be concise; avoid redundancy between sections
- Do not invent information not present in Confluence or the file list
- If a Confluence section is an unfilled template placeholder, skip it silently
