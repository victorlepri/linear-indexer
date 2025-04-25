import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import re
from initiatives import INITIATIVES
import json

# Load environment variables
load_dotenv()

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")

# Linear GraphQL endpoint
LINEAR_API_URL = "https://api.linear.app/graphql"

# GraphQL query to fetch project data with creator details
QUERY = """
query {
  projects(first: 100) {
    nodes {
      id
      name
      state
      createdAt
      creator {
        name
        displayName
        email
      }
    }
  }
}
"""

def fetch_projects():
    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(LINEAR_API_URL, json={"query": QUERY}, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]["projects"]["nodes"]

def extract_initiative_index(initiative, name):
    match = re.match(rf"{re.escape(initiative)}[\s-]*(\d{{3}})", name.upper())
    return int(match.group(1)) if match else None

def rename_project(project_id, new_name):
    mutation = """
    mutation RenameProject($id: String!, $name: String!) {
      projectUpdate(id: $id, input: { name: $name }) {
        success
        project {
          id
          name
        }
      }
    }
    """
    variables = {"id": project_id, "name": new_name}
    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(LINEAR_API_URL, json={"query": mutation, "variables": variables}, headers=headers)

if __name__ == "__main__":
    # Load existing project_database.json for appending new data
    try:
        with open("project_database.json", "r") as f:
            content = f.read().strip()
            existing_data = json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    projects = fetch_projects()
    initiative_indices = {initiative: 0 for initiative in INITIATIVES}

    for p in projects:
        name_upper = p["name"].upper()
        for initiative in INITIATIVES:
            if name_upper.startswith(initiative):
                num = extract_initiative_index(initiative, p["name"])
                if num is not None and num > initiative_indices[initiative]:
                    initiative_indices[initiative] = num

    matching_projects = []
    for p in projects:
        name_upper = p["name"].upper()
        state = p["state"].lower()
        if state not in ["planned", "started", "completed"]:
            continue
        for initiative in INITIATIVES:
            if name_upper.startswith(initiative):
                matching_projects.append((initiative, p))
                break

    matching_projects.sort(key=lambda ip: datetime.strptime(ip[1]["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"))

    project_db = []

    for initiative, p in matching_projects:
        if extract_initiative_index(initiative, p["name"]) is None:
            cleaned_name = re.sub(r"(?i)^" + re.escape(initiative) + r"[\s-]*", "", p["name"]).strip()
            initiative_indices[initiative] += 1
            padded_index = f"{initiative_indices[initiative]:03d}"
            new_name = f"{initiative}-{padded_index} {cleaned_name}"
            rename_project(p["id"], new_name)
            creator_info = p.get("creator", {})
            created_by = creator_info.get("name") or creator_info.get("displayName") or "Unknown"
            created_by_email = creator_info.get("email", "Unknown")
            project_db.append({
                "initiative": initiative,
                "index": padded_index,
                "name": new_name,
                "createdAt": p["createdAt"],
                "createdBy": created_by,
                "createdByEmail": created_by_email
            })

    if project_db:
        existing_data.extend(project_db)

        with open("project_database.json", "w") as f:
            json.dump(existing_data, f, indent=2)