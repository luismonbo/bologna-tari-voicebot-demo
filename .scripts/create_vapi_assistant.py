#!/usr/bin/env python3
"""
Create or update the Vapi assistant from vapi/assistant.json.
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_BASE_URL = "https://api.vapi.ai"
ASSISTANT_JSON_PATH = project_root / "vapi" / "assistant.json"


def get_api_key() -> str:
    """Get VAPI_API_KEY from env or prompt user."""
    if VAPI_API_KEY:
        print(f"✓ Loaded VAPI_API_KEY from environment")
        return VAPI_API_KEY

    api_key = input("Enter your VAPI_API_KEY: ").strip()
    if not api_key:
        print("Error: VAPI_API_KEY is required")
        sys.exit(1)
    return api_key


def load_assistant_config(path: Path) -> dict:
    """Load assistant config from JSON file."""
    if not path.exists():
        print(f"Error: {path} not found")
        sys.exit(1)

    with open(path) as f:
        config = json.load(f)

    print(f"✓ Loaded assistant config from {path}")
    return config


def create_or_update_assistant(api_key: str, assistant_config: dict) -> dict:
    """Create or update assistant in Vapi."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    assistant_id = assistant_config.get("id")

    if assistant_id:
        # Update existing
        print(f"\nUpdating assistant: {assistant_id}")
        url = f"{VAPI_BASE_URL}/assistant/{assistant_id}"
        response = requests.put(url, json=assistant_config, headers=headers)
    else:
        # Create new
        print("\nCreating new assistant...")
        url = f"{VAPI_BASE_URL}/assistant"
        # Remove system fields for creation
        payload = {
            k: v for k, v in assistant_config.items()
            if k not in ["id", "orgId", "createdAt", "updatedAt"]
        }
        response = requests.post(url, json=payload, headers=headers)

    if response.status_code not in [200, 201]:
        print(f"✗ Error ({response.status_code}): {response.text}")
        sys.exit(1)

    result = response.json()
    return result


def main():
    """Main entry point."""
    api_key = get_api_key()
    assistant_config = load_assistant_config(ASSISTANT_JSON_PATH)

    result = create_or_update_assistant(api_key, assistant_config)

    print("\n" + "=" * 60)
    print("✓ SUCCESS")
    print("=" * 60)
    print(f"Assistant ID: {result.get('id')}")
    print(f"Name: {result.get('name')}")
    print(f"Voice: {result.get('voice', {}).get('voiceId')}")
    print(f"Tools: {len(result.get('model', {}).get('toolIds', []))} configured")
    print(f"Updated: {result.get('updatedAt')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
