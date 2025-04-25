# 🧭 Linear Project Indexer

Automatically index and rename Linear projects based on initiative codes like `INITIATIVE1`, `INITIATIVE2`, etc.

This script fetches projects from Linear, assigns the next available number for each initiative, renames the project accordingly, and logs metadata in a local JSON database.

---

## ✨ Features

- ✅ Automatically detects and renames projects missing index numbers
- 📈 Maintains independent counters per initiative (e.g. `INITIATIVE1-001`, `INITIATIVE2-001`)
- 🗃 Appends a structured log of all renamed projects to `project_database.json`
- 🧠 Tracks initiative, index, name, creation date, creator name and email (based on Linear data only)
- ⚡ Simple to configure and run locally

---

## 🔧 Setup

### 1. Clone the repo

```bash
git clone https://github.com/victorlepri/linear-indexing.git
cd linear-indexing
```

### 2. Install dependencies

Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> If `requirements.txt` doesn't exist, install manually:
```bash
pip install requests python-dotenv
```

### 3. Add your Linear API key

Create a `.env` file:

```env
LINEAR_API_KEY=your_linear_api_key_here
```

Generate a token from [Linear's API settings](https://linear.app/settings/api).

---

## 🧭 Configure Initiatives

In the `initiatives.py` file, list the initiative prefixes you want to track:

```python
INITIATIVES = ["INITIATIVE1", "INITIATIVE2"]
```

Each initiative will maintain its own index sequence.

> **Important:** For this script to properly detect and index your projects, the project name in Linear **must begin with the initiative prefix**, such as `INITIATIVE1`, `INITIATIVE2`, etc.  
> Example: `INITIATIVE1 - Add EVM support` or `INITIATIVE2 - Revamp onboarding`

---

## 🚀 Running the Script

```bash
python generate_index.py
```

What it does:
- Fetches all projects
- Filters by status: `planned`, `started`, or `completed`
- Detects missing numbers after initiative prefix
- Renames the project via the Linear API based on initiative patterns found in the name
- Calculates the next number using current projects in Linear, regardless of what's in the database
- Appends renamed project metadata to `project_database.json`

> Note: The script silently appends to the local database without printing to console unless an error occurs.

---

## 🧾 Example Rename

A project titled:

```
INITIATIVE1 - Auto Indexer
```

Will be renamed to:

```
INITITATIVE1-003 Auto Indexer
```

---

## 🗃 Output

Appends structured data to `project_database.json`:

```json
{
  "initiative": "INITIATIVE1",
  "index": "003",
  "name": "INITIATIVE1-003 Auto Indexer",
  "createdAt": "2025-04-25T14:00:00Z",
  "createdBy": "Victor Lepri",
  "createdByEmail": "victor@example.com"
}
```

---

## 📦 Git Ignore

Your `.gitignore` should include:

```
.venv/
.env
__pycache__/
*.pyc
project_database.json
```

---

## ℹ️ Note on Initiatives

As of now, Linear's public API does not support fetching or assigning initiatives programmatically.

To work around this:
- We use a naming convention to simulate initiative tracking.
- Initiatives like `INITIATIVE1`, `INITIATIVE2`, etc. are hard-coded in the `initiatives.py` file.
- The script looks for project names that begin with these initiative codes and applies indexing logic accordingly.

Once Linear releases initiative support in their API, this logic can be updated to fetch and assign real initiatives dynamically.

---

[@victorlepri](https://github.com/victorlepri)

👾
