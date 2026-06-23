"""Debug script to test different TARI URLs and see what content is available."""

import os
from scrapegraphai.graphs import SmartScraperGraph

# Test URLs - try different ones to find TARI content
URLS_TO_TEST = [
    "https://www.comune.bologna.it/servizi/tasse-tributi/riduzione-tari-unico-occupante",
    "https://www.comune.bologna.it/servizi/tasse-tributi",
    "https://www.comune.bologna.it/servizi/casa",
    "https://www.comune.bologna.it/servizi/casa/dichiarazione-tari",
    "https://www.comune.bologna.it/amministrazione/uffici/ufficio-tassa-rifiuti",
]

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("[ERROR] OPENAI_API_KEY not set")
    exit(1)

graph_config = {
    "llm": {
        "api_key": api_key,
        "model": "openai/gpt-4o-mini",
    },
    "verbose": False,
    "headless": True,
}

for url in URLS_TO_TEST:
    print(f"\n{'='*70}")
    print(f"Testing: {url}")
    print(f"{'='*70}")

    try:
        scraper = SmartScraperGraph(
            prompt="Extract all text content about TARI from this page. Output only the main content, not navigation or headers.",
            source=url,
            config=graph_config,
        )

        result = scraper.run()

        # Check what we got
        if isinstance(result, dict):
            content = result.get("content", "")
        else:
            content = str(result)

        if not content or content == "NA":
            print("[NO CONTENT] Scraper returned empty/NA")
        else:
            # Show first 500 chars
            print(f"[OK] Got content ({len(content)} chars):")
            print(content[:500])
            if len(content) > 500:
                print(f"... ({len(content) - 500} more chars)")

    except Exception as e:
        print(f"[ERROR] {e}")

print(f"\n{'='*70}")
print("Testing complete. Which URLs had useful content?")
