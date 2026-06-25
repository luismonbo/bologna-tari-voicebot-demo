#!/usr/bin/env python3
"""
Setup Vapi assistant and tools from scratch.

Flow:
1. Create the four tools (query_services, check_availability, create_appointment, lookup_appointment)
2. Create the assistant with those tools
3. Save the assistant config back to vapi/assistant.json
4. Report success/failure

Required environment variables:
  - VAPI_PRIVATE_API_KEY: Your Vapi API key
  - BACKEND_PUBLIC_URL: Public URL of your backend (e.g., ngrok URL) — MUST be internet-accessible
"""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import find_dotenv, load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(find_dotenv(project_root / ".env"))

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_API_KEY")
VAPI_BASE_URL = "https://api.vapi.ai"
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL")
ASSISTANT_JSON_PATH = project_root / "vapi" / "assistant.json"


# Tool definitions matching PLAN.md §4
def get_tool_definitions(backend_url: str) -> list[dict]:
    """Generate tool definitions with backend URL (for creation)."""
    return [
        {
            "type": "apiRequest",
            "name": "query_services_test",
            "description": "Query the TARI knowledge base for information about waste tax services",
            "url": f"{backend_url}/tools/query_services",
            "method": "POST",
            "messages": [
                {
                    "type": "request-start",
                    "content": "Un momento...",
                },
                {
                    "type": "request-complete",
                    "content": "Ho completato la richiesta.",
                },
                {
                    "type": "request-failed",
                    "content": "Mi scuso, non riesco a elaborare la richiesta in questo momento.",
                },
                {
                    "type": "request-response-delayed",
                    "content": "Sto ancora elaborando...",
                },
            ],
        },
        {
            "type": "apiRequest",
            "name": "check_availability_test",
            "description": "Check availability of appointment slots for a given office and date",
            "url": f"{backend_url}/tools/check_availability",
            "method": "POST",
            "messages": [
                {
                    "type": "request-start",
                    "content": "Un momento...",
                },
                {
                    "type": "request-complete",
                    "content": "Ho completato la richiesta.",
                },
                {
                    "type": "request-failed",
                    "content": "Mi scuso, non riesco a elaborare la richiesta in questo momento.",
                },
                {
                    "type": "request-response-delayed",
                    "content": "Sto ancora elaborando...",
                },
            ],
        },
        {
            "type": "apiRequest",
            "name": "create_appointment_test",
            "description": "Create an appointment at the specified office",
            "url": f"{backend_url}/tools/create_appointment",
            "method": "POST",
            "messages": [
                {
                    "type": "request-start",
                    "content": "Un momento...",
                },
                {
                    "type": "request-complete",
                    "content": "Ho completato la richiesta.",
                },
                {
                    "type": "request-failed",
                    "content": "Mi scuso, non riesco a elaborare la richiesta in questo momento.",
                },
                {
                    "type": "request-response-delayed",
                    "content": "Sto ancora elaborando...",
                },
            ],
        },
        {
            "type": "apiRequest",
            "name": "lookup_appointment_test",
            "description": "Look up an existing appointment",
            "url": f"{backend_url}/tools/lookup_appointment",
            "method": "POST",
            "messages": [
                {
                    "type": "request-start",
                    "content": "Un momento...",
                },
                {
                    "type": "request-complete",
                    "content": "Ho completato la richiesta.",
                },
                {
                    "type": "request-failed",
                    "content": "Mi scuso, non riesco a elaborare la richiesta in questo momento.",
                },
                {
                    "type": "request-response-delayed",
                    "content": "Sto ancora elaborando...",
                },
            ],
        },
    ]


def get_api_key() -> str:
    """Get VAPI_PRIVATE_API_KEY from env or prompt user."""
    if VAPI_API_KEY:
        print("✓ Loaded VAPI_PRIVATE_API_KEY from environment")
        return VAPI_API_KEY

    api_key = input("Enter your VAPI_PRIVATE_API_KEY: ").strip()
    if not api_key:
        print("✗ Error: VAPI_PRIVATE_API_KEY is required")
        sys.exit(1)
    return api_key


def get_backend_url() -> str:
    """Get BACKEND_PUBLIC_URL from env or prompt user."""
    if BACKEND_PUBLIC_URL:
        if BACKEND_PUBLIC_URL.startswith("http://localhost"):
            print("⚠ Warning: BACKEND_PUBLIC_URL is localhost. Vapi needs a public URL!")
            print("  Start ngrok: ngrok http 8000")
            print("  Then set: BACKEND_PUBLIC_URL=https://your-ngrok-id.ngrok.io")
        else:
            print(f"✓ Using BACKEND_PUBLIC_URL: {BACKEND_PUBLIC_URL}")
        return BACKEND_PUBLIC_URL

    url = input("Enter your BACKEND_PUBLIC_URL (e.g., https://your-ngrok-id.ngrok.io): ").strip()
    if not url:
        print("✗ Error: BACKEND_PUBLIC_URL is required (must be internet-accessible)")
        sys.exit(1)
    return url


def load_assistant_template(path: Path) -> dict:
    """Load assistant config template from JSON file."""
    if not path.exists():
        print(f"✗ Error: {path} not found")
        sys.exit(1)

    with open(path) as f:
        config = json.load(f)

    print(f"✓ Loaded assistant template from {path}")
    return config


def create_tools(api_key: str, tool_definitions: list[dict]) -> list[str]:
    """
    Create tools in Vapi and return their IDs.

    Returns a list of tool IDs.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    tool_ids = []

    for tool_def in tool_definitions:
        print(f"\n▶ Creating tool: {tool_def['name']}")
        url = f"{VAPI_BASE_URL}/tool"
        response = httpx.post(url, json=tool_def, headers=headers, timeout=30.0)

        if response.status_code not in [200, 201]:
            print(f"✗ Error ({response.status_code}): {response.text}")
            sys.exit(1)

        result = response.json()
        tool_id = result.get("id")
        tool_ids.append(tool_id)
        print(f"✓ Created tool: {tool_id}")

    return tool_ids


def create_assistant_with_tool_ids(
    api_key: str, assistant_config: dict, tool_ids: list[str]
) -> dict:
    """
    Create or update assistant referencing existing tool IDs.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    assistant_id = assistant_config.get("id")

    # Prepare payload, removing server-generated fields
    payload = {
        k: v
        for k, v in assistant_config.items()
        if k not in ["id", "orgId", "createdAt", "updatedAt", "isServerUrlSecretSet"]
    }

    # Inject tool IDs into the model section
    if "model" not in payload:
        payload["model"] = {}

    payload["model"]["toolIds"] = tool_ids

    if assistant_id:
        # Update existing
        print(f"\n▶ Updating assistant: {assistant_id}")
        url = f"{VAPI_BASE_URL}/assistant/{assistant_id}"
        response = httpx.put(url, json=payload, headers=headers, timeout=30.0)
    else:
        # Create new
        print("\n▶ Creating new assistant with tool IDs...")
        url = f"{VAPI_BASE_URL}/assistant"
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)

    if response.status_code not in [200, 201]:
        print(f"✗ Error ({response.status_code}): {response.text}")
        sys.exit(1)

    result = response.json()
    return result


def save_assistant_config(path: Path, config: dict) -> None:
    """Save assistant config back to JSON file."""
    # Pretty-print with 2-space indentation
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ Saved assistant config to {path}")


def main() -> None:
    """Main entry point: two-phase setup (create tools, then wire to assistant)."""
    print("=" * 70)
    print("VAPI Assistant & Tools Setup")
    print("=" * 70)

    api_key = get_api_key()
    backend_url = get_backend_url()

    # Phase 1: Create the tools
    print(f"\n{'=' * 70}")
    print("Phase 1: Creating tools")
    print("=" * 70)
    tool_definitions = get_tool_definitions(backend_url)
    print(f"▶ Creating {len(tool_definitions)} tools:")
    for tool in tool_definitions:
        print(f"  - {tool['name']}: {tool['url']}")

    tool_ids = create_tools(api_key, tool_definitions)

    # Phase 2: Create/update assistant with the tool IDs
    print(f"\n{'=' * 70}")
    print("Phase 2: Wiring assistant to tools")
    print("=" * 70)
    assistant_config = load_assistant_template(ASSISTANT_JSON_PATH)

    result = create_assistant_with_tool_ids(api_key, assistant_config, tool_ids)

    # Save the result (with all Vapi metadata, including tool IDs)
    save_assistant_config(ASSISTANT_JSON_PATH, result)

    # Print success report
    print("\n" + "=" * 70)
    print("✓ SUCCESS")
    print("=" * 70)
    print(f"Assistant ID: {result.get('id')}")
    print(f"Name: {result.get('name')}")
    print(f"Voice: {result.get('voice', {}).get('voiceId')}")

    wired_tool_ids = result.get("model", {}).get("toolIds", [])
    print(f"\nTools wired to assistant: {len(wired_tool_ids)}")
    for i, tool_id in enumerate(wired_tool_ids, 1):
        print(f"  {i}. {tool_id}")

    print(f"\nAssistant created: {result.get('createdAt')}")
    print(f"Last updated: {result.get('updatedAt')}")
    print("=" * 70)
    print("\nNext steps:")
    print(f"1. Set ASSISTANT_ID={result.get('id')} in your .env")
    print("2. Keep ngrok running: ngrok http 8000")
    print("3. Update .env BACKEND_PUBLIC_URL to your ngrok URL")
    print(f"4. Assistant config is saved to: {ASSISTANT_JSON_PATH}")


if __name__ == "__main__":
    main()
