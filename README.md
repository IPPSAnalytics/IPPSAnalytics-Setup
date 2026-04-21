# IPPSAnalytics

This is the analytics monorepo for UCSD's Integrated Procurement, Payment, and Supply (IPPS) department. It contains ~60 independent analytics projects spanning procurement, disbursements, logistics, sourcing, and data mart pipelines.

Each subfolder is its own Git repository, independently versioned and owned by a team or business unit. This root folder serves as the local workspace that aggregates all of them in one place.

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

This will pull down every repository in the IPPSAnalytics GitHub organization into a single local folder (defaults to `~/Desktop/IPPSAnalytics`). You only need to do this once.

To specify a custom destination:

```bash
./clone_org.sh /path/to/your/folder
```

### Step 2 — Stay Up to Date

When you return to work after time away, or want to sync all projects with their latest changes from GitHub, run:

```bash
./update_all.sh
```

This runs `git pull` on every subfolder that is a Git repository and prints a summary of what updated, what failed, and what was skipped.

---

## Scripts

### `clone_org.sh`
**Use when:** You are setting up this workspace for the first time, or a new team member needs to get the full repo locally.

Queries the IPPSAnalytics GitHub organization via the GitHub CLI and clones every repository into the destination folder. Skips any repo that has already been cloned. Requires `gh` to be installed and authenticated.

### `update_all.sh`
**Use when:** You want to pull the latest changes across all projects at once — useful at the start of a work session or after a sprint where multiple projects were updated.

Iterates every subfolder, checks if it is a Git repository, and runs `git pull` on each. Reports success, failure, and skipped folders (non-Git directories like config files) with a final summary.

---

## Project Structure

Each project folder follows this naming convention:

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

Always read a project's `README.md` first before working in it.
