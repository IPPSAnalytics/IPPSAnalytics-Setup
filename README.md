# IPPSAnalytics-Setup

This repo contains the setup scripts, Confluence sync tooling, and project standards for the IPPSAnalytics monorepo at UCSD's Integrated Procurement, Payment, and Supply (IPPS) department.

The monorepo itself contains ~60 independent analytics projects. Each project lives in its own subfolder and Git repository. This setup repo provides the tools to manage them all from one place.

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

This will pull down every repository in the IPPSAnalytics GitHub organization into a single local folder. You only need to do this once.

To specify a custom destination:

```bash
./clone_org.sh /path/to/your/folder
```

### Step 2 — Install Python Dependencies

The Confluence sync tooling requires two Python packages:

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

When you return to work after time away, or want to sync all projects with their latest changes from GitHub, run:

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

### `/audit-project [project number]`
Performs a code-level audit of a project. Reads every SQL and notebook file, adds or fixes comments, and flags notebooks that qualify for conversion to `.py` — all per the rules in `project-standards.md`.

### `/full-review [project number]`
Runs both of the above in sequence: README first, then file/folder checks, then code audit. Confirms with you at each step before making changes.

**Example:**
```
/full-review 725
```

---

## Project Standards

`project-standards.md` is the single file that defines how Claude handles every project. It covers:

- **README structure** — required sections and how to populate them from Confluence
- **File & folder checks** — naming conventions and required files
- **Code comments** — rules for SQL headers and notebook Markdown cells
- **Notebook conversion** — criteria for converting `.ipynb` to `.py`
- **Tone & style** — writing guidelines

Edit this file to change what gets checked or generated across all projects. No other files need to change.

---

## Further Reading

See `HOW_IT_WORKS.md` for a detailed explanation of how all the pieces fit together, including a diagram of the full data flow from Confluence to README.

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
