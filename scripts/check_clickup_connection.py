#!/usr/bin/env python3
"""
ClickUp API read-only connection check.

Usage:
    python scripts/check_clickup_connection.py

Loads environment variables from .env (if python-dotenv is installed),
validates required variables, then fetches workspace metadata via
the ClickUp v2 API.

Safe output only:
  - workspace/team ID
  - space names and IDs
  - folder names and IDs
  - list names and IDs
  - task counts, names, status, and priority

Never prints the API token.
Never performs write operations.
Exits gracefully when credentials are missing.
"""
from __future__ import annotations
import os
import sys

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env must be pre-loaded in the shell environment

try:
    import requests
except ImportError:
    print("Error: 'requests' package required.")
    print("Install it with: pip install requests")
    sys.exit(1)

_BASE_URL = "https://api.clickup.com/api/v2"

_REQUIRED_VARS = [
    "CLICKUP_API_TOKEN",
    "CLICKUP_TEAM_ID",
]

_LIST_VARS = [
    ("CLICKUP_LIST_BACKLOG_REQUIREMENTS_ID", "Backlog & Requirements"),
    ("CLICKUP_LIST_SDLC_RISK_REVIEW_ID", "SDLC Risk Review"),
    ("CLICKUP_LIST_QA_DOD_VALIDATION_ID", "QA / DoD Validation"),
    ("CLICKUP_LIST_GOVERNANCE_HITL_ID", "Governance & HITL"),
    ("CLICKUP_LIST_DEMO_DASHBOARD_ID", "Demo Dashboard"),
]


def _headers() -> dict[str, str]:
    # Token is read from env and used only as an Authorization header — never printed
    return {"Authorization": os.environ["CLICKUP_API_TOKEN"]}


def _get(url: str) -> dict:
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.SSLError:
        print("SSL error: certificate verification failed.")
        print("On Windows, try: pip install python-certifi-win32")
        print("Or set REQUESTS_CA_BUNDLE to your certificate bundle path.")
        sys.exit(1)
    except requests.exceptions.ConnectionError as exc:
        print(f"Connection error: {type(exc).__name__}")
        print("Check your network connection and that api.clickup.com is reachable.")
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        if status == 401:
            print("Authentication failed (HTTP 401). Check your CLICKUP_API_TOKEN.")
        elif status == 403:
            print("Access denied (HTTP 403). Check your token permissions.")
        else:
            print(f"HTTP error: {status}")
        sys.exit(1)


def main() -> None:
    # Validate required variables
    missing = [v for v in _REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print("Missing required environment variables:")
        for v in missing:
            print(f"  {v}")
        print()
        print("Configure these in your local .env file (see .env.example for the template).")
        print("Mock/demo mode continues to work without ClickUp credentials.")
        sys.exit(1)

    team_id = os.environ["CLICKUP_TEAM_ID"]
    mode = os.environ.get("CLICKUP_INTEGRATION_MODE", "readonly")
    print(f"Team ID          : {team_id}")
    print(f"Integration mode : {mode}")
    print()

    # Fetch spaces
    print("Spaces in workspace:")
    data = _get(f"{_BASE_URL}/team/{team_id}/space?archived=false")
    for space in data.get("spaces", []):
        print(f"  {space['name']} (ID: {space['id']})")

    # Fetch folders in configured space
    space_id = os.environ.get("CLICKUP_SPACE_ID")
    if space_id:
        print(f"\nFolders in space {space_id}:")
        data = _get(f"{_BASE_URL}/space/{space_id}/folder?archived=false")
        for folder in data.get("folders", []):
            print(f"  {folder['name']} (ID: {folder['id']})")

    # Fetch lists in configured folder
    folder_id = os.environ.get("CLICKUP_FOLDER_ID")
    if folder_id:
        print(f"\nLists in folder {folder_id}:")
        data = _get(f"{_BASE_URL}/folder/{folder_id}/list?archived=false")
        for lst in data.get("lists", []):
            task_count = lst.get("task_count", "?")
            print(f"  {lst['name']} (ID: {lst['id']}, tasks: {task_count})")

    # Fetch task details from each configured list
    configured_lists = [(var, label) for var, label in _LIST_VARS if os.environ.get(var)]
    if configured_lists:
        print("\nTasks per configured list:")
        for var, label in configured_lists:
            list_id = os.environ[var]
            try:
                data = _get(f"{_BASE_URL}/list/{list_id}/task")
                tasks = data.get("tasks", [])
                print(f"\n  [{label}] — {len(tasks)} task(s)")
                for task in tasks:
                    name = task.get("name", "(no name)")
                    status_raw = task.get("status") or {}
                    status = status_raw.get("status", "unknown") if isinstance(status_raw, dict) else str(status_raw)
                    priority_raw = task.get("priority")
                    priority = priority_raw.get("priority", "none") if isinstance(priority_raw, dict) else "none"
                    print(f"    - {name} | status: {status} | priority: {priority}")
            except requests.HTTPError as exc:
                print(f"  [{label}] — HTTP error: {exc.response.status_code}")
            except requests.RequestException as exc:
                print(f"  [{label}] — Request error: {type(exc).__name__}")

    print("\nRead-only connection check complete. No write operations were performed.")


if __name__ == "__main__":
    main()
