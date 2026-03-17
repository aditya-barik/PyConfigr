#!/usr/bin/env python3
"""
Setup GitHub labels for PyConfigr repository.

Usage:
    python setup_labels.py <repo_owner> <repo_name> <github_token>

Example:
    python setup_labels.py aditya-barik PyConfigr ghp_xxxxxxxxxxxx

Requirements:
    pip install requests
"""

import json
import sys
from pathlib import Path

import requests


def load_labels_config(config_file: str) -> list[dict]:
    """Load labels configuration from JSON file."""
    with open(config_file, "r") as f:
        config = json.load(f)
    return config["labels"]


def create_labels(owner: str, repo: str, token: str, labels: list[dict]) -> None:
    """Create labels in GitHub repository."""
    base_url = f"https://api.github.com/repos/{owner}/{repo}/labels"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    created = 0
    updated = 0
    failed = 0

    for label in labels:
        payload = {
            "name": label["name"],
            "color": label["color"],
            "description": label["description"],
        }

        # Try to update first (in case label exists)
        update_url = f"{base_url}/{label['name']}"
        response = requests.patch(update_url, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"✅ Updated label: {label['name']}")
            updated += 1
        elif response.status_code == 404:
            # Label doesn't exist, create it
            response = requests.post(base_url, json=payload, headers=headers)
            if response.status_code == 201:
                print(f"✨ Created label: {label['name']}")
                created += 1
            else:
                print(f"❌ Failed to create label: {label['name']}")
                print(f"   Response: {response.status_code} - {response.text}")
                failed += 1
        else:
            print(f"❌ Failed to update label: {label['name']}")
            print(f"   Response: {response.status_code} - {response.text}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Summary: {created} created, {updated} updated, {failed} failed")
    print("=" * 50)


def main():
    if len(sys.argv) != 4:
        print("Usage: python setup_labels.py <owner> <repo> <github_token>")
        print("Example: python setup_labels.py aditya-barik PyConfigr ghp_xxxx")
        sys.exit(1)

    owner, repo, token = sys.argv[1], sys.argv[2], sys.argv[3]

    # Find labels.json in .github directory
    script_dir = Path(__file__).parent.parent
    config_file = (
        script_dir / ".github" / "automations" / "auto_labelling" / "labels.json"
    )

    if not config_file.exists():
        print(f"❌ Error: {config_file} not found")
        sys.exit(1)

    print(f"Loading labels from {config_file}...")
    labels = load_labels_config(config_file)
    print(f"Found {len(labels)} labels to create/update\n")

    print(f"Setting up labels for {owner}/{repo}...\n")
    create_labels(owner, repo, token, labels)


if __name__ == "__main__":
    main()
