# IPPSAnalytics-Setup

This repo contains the setup scripts, Confluence sync tooling, and project standards for the IPPSAnalytics monorepo at UCSD's Integrated Procurement, Payment, and Supply (IPPS) department.

The monorepo contains ~60 independent analytics projects. Each project lives in its own subfolder and Git repository. This setup repo provides the tools to manage them all from one place.

---

## Project Goals

These are the documentation and quality standards this tooling is designed to enforce across every project:

1. **Data flow documentation** — every project README should describe where data comes from, how it moves through the pipeline, and what it produces (e.g. `707-DM-SNOW_Cases`)
2. **Inputs and outputs** — explicitly document what files or tables feed the script and what the expected output is
3. **Code comments** — scripts should be readable to new team members; SQL and notebooks follow the comment rules in `project-standards.md`
4. **Business logic** — tie each project to its Confluence page (same first 3 digits as the folder name); use the main project page for general context and meeting notes for recurring run history
5. **Notebook to `.py` conversion** — pure transformation notebooks with no visual output are candidates for conversion; see `project-standards.md` for criteria
6. **Field updates** — when new fields are added, the script and README are updated together

---

## How the Workflow Fits Together

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

## Getting Started (New Team Member)

### Prerequisites

- **Git** — [git-scm.com](https://git-scm.com)
- **GitHub CLI (`gh`)** — [cli.github.com](https://cli.github.com) — used to authenticate and interact with the IPPSAnalytics GitHub organization
  - Install on Mac: `brew install gh`
  - After installing, authenticate: `gh auth login`
  - You must have been granted access to the **IPPSAnalytics** GitHub organization by an admin
- **Python + Jupyter** — for running `.ipynb` notebooks (recommended: install via [Anaconda](https://www.anaconda.com/))
- **Oracle DB access** — required to run any `Q-*.sql` query files; coordinate with your team lead
- **L-drive access** — notebooks reference Windows network paths (`L:\TEAMS\pur\ANALYTICS\Projects\`); must be mounted or mapped on your machine

### Step 1 — Clone All Repos

Run the following from wherever you want your local workspace to live:

```bash
./clone_org.sh
```

This pulls down every repository in the IPPSAnalytics GitHub organization into a single local folder. You only need to do this once.

To specify a custom destination:

```bash
./clone_org.sh /path/to/your/folder
```

### Step 2 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure Credentials

Copy your Confluence API token into the `.env` file:

```
CONFLUENCE_EMAIL=your-ucsd-email@ucsd.edu
API_KEY=your-api-token
```

Get an API token at: `id.atlassian.com/manage-profile/security/api-tokens`

The `.env` file is gitignored and will never be committed.

### Step 4 — Stay Up to Date

When you return to work after time away, or want to sync all projects with their latest changes from GitHub:

```bash
./update_all.sh
```

This runs `git pull` on every subfolder that is a Git repository and prints a summary of what updated, what failed, and what was skipped.

---

## Scripts

### `clone_org.sh`
**Use when:** Setting up the workspace for the first time, or a new team member needs to get everything locally.

Queries the IPPSAnalytics GitHub organization via the GitHub CLI and clones every repository into the destination folder. Skips any repo that has already been cloned.

### `update_all.sh`
**Use when:** You want to pull the latest changes across all projects at once — useful at the start of a work session or after a sprint where multiple projects were updated.

Iterates every subfolder, checks if it is a Git repository, and runs `git pull` on each. Reports success, failure, and skipped folders with a final summary.

### `sync_readmes.py`
**Use when:** You want to generate or refresh README files for project repos using content from Confluence.

Connects to the IPPS Confluence space, finds the page matching a project number, converts the content to Markdown, and writes it to the project's `README.md`.

```bash
# Sync all matched projects
python sync_readmes.py

# Sync one project
python sync_readmes.py --project 725

# Preview without writing files
python sync_readmes.py --dry-run

# Print Confluence content to stdout (used by Claude slash commands)
python sync_readmes.py --fetch-only 725
```

---

## Claude Code Slash Commands

This repo powers three Claude Code slash commands available anywhere in the workspace. All three read `project-standards.md` live at runtime, so editing that file changes their behavior immediately.

### `/sync-readme [project number]`
Generates or updates the `README.md` for a project. Pulls Confluence content, applies the README and file/folder rules from `project-standards.md`, and asks for confirmation before writing.

When you run `/sync-readme 725`, Claude:
1. Runs `sync_readmes.py --fetch-only 725` to pull the Confluence page for project 725
2. Reads `project-standards.md` for the current rules
3. Lists the actual files inside the `725-*` project folder
4. Generates the README and reports any file/folder issues
5. Asks whether to save, adjust, or move on

### `/audit-project [project number]`
Performs a code-level audit of a project. Reads every SQL and notebook file, adds or fixes comments, and flags notebooks that qualify for conversion to `.py` — all per the rules in `project-standards.md`.

### `/full-review [project number]`
Runs both of the above in sequence: README first, then file/folder checks, then code audit. Confirms with you at each step before making changes.

```
/full-review 725
```

---

## How to Add or Change Rules

Open `project-standards.md` and edit it directly. Examples:

- A new required README section (e.g. "Scheduling" for projects that run on a cron)
- A new file convention check (e.g. "every project must have a `.gitignore`")
- A rule about what to do when a Confluence page is missing
- Instructions for how to handle a specific department's naming quirks

No other files need to change — the slash commands always read the latest version of `project-standards.md` at runtime.

---

## Bulk Sync (Without Claude)

To write READMEs for all matched projects at once without Claude's customization step:

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

Pages are matched to repo folders by project number (e.g. folder `725-DIS-PaymentWorks_Metrics_Supplier_Set_Up` matches any Confluence page whose title contains `725`). Common title formats:

| Format | Example |
|---|---|
| `BI - [num] [name]` | `BI - 725 PaymentWorks Metrics and Supplier Set-Up` |
| `OFC-[num] [name]` | `OFC-755 Payment Status to Payment Compass` |
| `IPPS-[num] [name]` | `IPPS-602 Not Validated Invoices` |

---

## Project Structure

Each project folder in the monorepo follows this naming convention:

```
[ID]-[DEPT]-[Description]/
  Q-[ID]-*.sql       # Oracle queries (data extraction)
  S-[ID]-*.ipynb     # Script/transformation notebooks
  P-[ID]-*.sql       # Stored procedures
  T-[ID]-*.ipynb     # Test/temp notebooks
  main.ipynb         # Orchestration entry point (when present)
  README.md          # Project description, JIRA links, data sources
```

Department codes: `DM` (Data Marts), `DIS` (Disbursements), `SPROC` (Sourcing/Procurement), `LOG` (Logistics), `INT` (Integrations), `SB` (Small Business), `IPPS` (Executive), `CXM` (Customer Experience).
