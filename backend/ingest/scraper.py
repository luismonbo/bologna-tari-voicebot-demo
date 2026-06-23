"""Scrape TARI content from Comune di Bologna using ScrapeGraphAI."""

import json
import os
from pathlib import Path

from scrapegraphai.graphs import SmartScraperGraph

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def scrape_tari_content():
    """Scrape TARI-related pages from Comune di Bologna."""

    urls = [
        "https://www.comune.bologna.it/servizi/tasse-tributi/riduzione-tari-unico-occupante",
        "https://www.comune.bologna.it/servizi/tasse-tributi/pagare-tassa-rifiuti-tari",
    ]

    # Configure with OpenAI API (or switch to Ollama if OPENAI_API_KEY not set)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Using Ollama (ollama/llama2)")
        graph_config = {
            "llm": {
                "model": "ollama/hf.co/unsloth/gemma-4-12b-it-GGUF:Q4_K_M",
                "model_tokens": 8192,
            },
            "verbose": True,
            "headless": True,
        }
    else:
        graph_config = {
            "llm": {
                "api_key": api_key,
                "model": "openai/gpt-5.4-mini",
            },
            "verbose": True,
            "headless": False,
        }

    for i, url in enumerate(urls):
        print(f"\n📄 Scraping ({i+1}/{len(urls)}): {url}")

        try:
            scraper = SmartScraperGraph(
                prompt=(
                    "Extract ALL text content from this page about TARI (Tassa sui Rifiuti). "
                    "Output the raw text exactly as it appears, preserving all details. "
                    "Do NOT summarize or describe the page. "
                    "Do NOT output navigation, headers, footers, or metadata. "
                    "Only output the actual content about TARI services, information, and procedures."
                ),
                source=url,
                config=graph_config,
            )

            result = scraper.run()

            # Debug: check if result is NA or empty
            if (
                result is None
                or result == "NA"
                or (isinstance(result, dict) and not result.get("content"))
            ):
                print(f"[WARNING] Scraper returned no content for {url}")
                print(f"[DEBUG] Result: {result}")

            # Save raw content
            filename = f"tari_{i:02d}_{url.split('/')[-1]}.json"
            filepath = DATA_DIR / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "source_url": url,
                        "content": result,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(f"[OK] Saved to {filepath}")

        except Exception as e:
            print(f"[ERROR] Scraping {url}: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    scrape_tari_content()
