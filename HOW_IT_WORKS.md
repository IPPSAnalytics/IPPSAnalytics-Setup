# How the IPPSAnalytics Repo Workflow Works

This document explains how the tools in `IPPSAnalytics-Setup/` fit together and how to use them.

---

## Overview

The goal of this workflow is to keep each project repo well-documented and consistently structured by pulling source-of-truth content from Confluence and applying a standard set of rules to every project folder.

```
Confluence (IPPS space)
        │
        │  sync_readmes.py --fetch-only
        ▼
  Project context (title, description, data sources, deliverables)
        │
        │  /sync-readme <project number>  (Claude Code slash command)
        ▼
  Claude reads project-standards.md + Confluence content + repo file list
        │
        ▼
  README.md written, file/folder issues flagged
```

---

## Files in This Folder

### `sync_readmes.py`
The core Python script. Connects to the Confluence REST API, searches the IPPS space for a page matching a project number, and converts the page content from HTML to Markdown.

**Modes:**
- `python sync_readmes.py` — syncs all matched projects, writing README.md to each folder directly
- `python sync_readmes.py --project 725` — syncs a single project
- `python sync_readmes.py --dry-run` — previews output without writing any files
- `python sync_readmes.py --fetch-only 725` — prints Confluence content to stdout for use in prompts

### `project-standards.md`
**The main file you will edit.** Defines the rules Claude follows when working on a project:
- What sections a README must contain and how to write them
- What file/folder conventions to enforce
- Tone and style guidelines

Any change you make here takes effect immediately the next time you run `/sync-readme`.

### `.env`
Stores credentials for the Confluence API. Never committed to git (covered by `.gitignore`).

```
CONFLUENCE_EMAIL=your-ucsd-email@ucsd.edu
API_KEY=your-api-token
```

### `requirements.txt`
Python dependencies for `sync_readmes.py`. Install with:
```bash
pip install -r requirements.txt
```

### `clone_org.sh`
Clones every repo in the IPPSAnalytics GitHub organization into your local workspace. Run once when setting up a new machine.

### `update_all.sh`
Pulls the latest changes across all project repos at once. Run at the start of a work session.

---

## The Slash Command: `/sync-readme`

`/sync-readme` is a Claude Code slash command stored at `.claude/commands/sync-readme.md` in the root of the workspace.

When you type `/sync-readme 725` in Claude Code, it:

1. Runs `sync_readmes.py --fetch-only 725` to pull the Confluence page for project 725
2. Reads `project-standards.md` for the current rules
3. Lists the actual files inside the `725-*` project folder
4. Passes all of that to Claude, which then generates the README and reports any file/folder issues
5. Asks you whether to save, adjust, or move on to another project

---

## How to Add or Change Rules

Open `project-standards.md` and edit it directly. Examples of things you can add:

- A new required README section (e.g. "Scheduling" for projects that run on a cron)
- A new file convention check (e.g. "every project must have a `.gitignore`")
- A rule about what to do when a Confluence page is missing
- Instructions for how to handle a specific department's naming quirks

No other files need to change — the slash command always reads the latest version of `project-standards.md` at runtime.

---

## How to Run a Bulk Sync (Without Claude)

If you want to write READMEs for all matched projects at once without Claude's customization step, run the script directly:

```bash
# Preview all projects
python sync_readmes.py --dry-run

# Write READMEs for all matched projects
python sync_readmes.py

# Write README for one project
python sync_readmes.py --project 725
```

This does a straight Confluence → Markdown dump without applying `project-standards.md`. Use the `/sync-readme` Claude workflow when you want intelligent, customized output.

---

## Confluence Space

All project pages live in the **IPPS** space on UCSD Collab:
`https://ucsdcollab.atlassian.net/wiki/spaces/IPPS/overview`

Pages are matched to repo folders by project number (e.g. folder `725-DIS-PaymentWorks_Metrics_Supplier_Set_Up` matches any Confluence page whose title contains `725`). Common title formats found in this space:

| Format | Example |
|---|---|
| `BI - [num] [name]` | `BI - 725 PaymentWorks Metrics and Supplier Set-Up` |
| `OFC-[num] [name]` | `OFC-755 Payment Status to Payment Compass` |
| `IPPS-[num] [name]` | `IPPS-602 Not Validated Invoices` |
