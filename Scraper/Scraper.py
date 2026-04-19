import os
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tavily import TavilyClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PLATFORMS = {
    "Flipkart": "site:flipkart.com",
    "Amazon": "site:amazon.in",
    "Croma": "site:croma.com",
    "Reliance Digital": "site:reliancedigital.in",
    "Vijay Sales": "site:vijaysales.com",
    "Tata Cliq": "site:tatacliq.com",
    "Poorvika": "site:poorvika.com",
    "Samsung Shop": "site:samsung.com/in",
}

EXTRACT_BATCH = 10

LISTING_URL = re.compile(
    r'(/blog|/blog-listing|/category|/collection/|search\?q=|[?&]sort=|/c/[a-z]|'
    r'all[-_]smartphones|best[-_]smartphones|[-_]phones[-_]under[-_]|'
    r'[-_]mobiles[-_]under|[-_]mobile[-_]under|upcoming[-_]mobile)',
    re.IGNORECASE
)
LISTING_TITLE = re.compile(
    r'(^best\s+mobile|^top\s+\d+|^upcoming\s+mobile|^shop\s+\w+\s+mobile\s+phone|'
    r'mobile\s+phones?\s+online|phones?\s+online\s+at\s+best|mobiles\s+online|'
    r'buy\s+\w+\s+mobiles\s+online)',
    re.IGNORECASE
)
BRAND_ALIASES = {
    'xiaomi':   ['xiaomi', 'redmi', 'poco'],
    'apple':    ['apple', 'iphone'],
    'motorola': ['motorola', 'moto'],
}

class Scraper:

    def __init__(self) -> None:
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search_platform(self, brand: str, budget: int, platform: str, site_filter: str) -> list:
        query = f"{brand} price under {budget} buy {site_filter} RAM storage specifications"
        try:
            response = self.client.search(
                query=query,
                max_results=10,
                search_depth="advanced",
                include_answer=False,
            )
            results = []
            for r in response.get("results", []):
                results.append({
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "platform": platform,
                })
            logging.info(f"Found {len(results)} results from {platform}.")
            return results
        except Exception as e:
            logging.error(f"Error searching {platform}: {e}")
            return []

    def extract_content(self, urls: list) -> dict:
        url_content = {}
        try:
            for i in range(0, len(urls), EXTRACT_BATCH):
                batch = urls[i:i + EXTRACT_BATCH]
                response = self.client.extract(urls=batch)
                for r in response.get("results", []):
                    if r.get("raw_content"):
                        url_content[r["url"]] = r["raw_content"][:3000]
            logging.info(f"Extracted actual page content for {len(url_content)} URLs.")
        except Exception as e:
            logging.error(f"Error during content extraction: {e}")
        return url_content

    def is_candidate(self, title: str, url: str, brand_core: str) -> bool:
        if LISTING_URL.search(url) or LISTING_TITLE.search(title):
            return False
        aliases = BRAND_ALIASES.get(brand_core, [brand_core])
        return any(a in title.lower() for a in aliases)

    def run(self, brand: str, budget: int) -> list:
        all_results = []
        with ThreadPoolExecutor(max_workers=len(PLATFORMS)) as executor:
            futures = {
                executor.submit(self.search_platform, brand, budget, platform, site_filter): platform
                for platform, site_filter in PLATFORMS.items()
            }
            for future in as_completed(futures):
                all_results.extend(future.result())
        logging.info(f"Total raw results collected: {len(all_results)}")

        brand_core = brand.lower().replace(' smartphones', '').replace(' smartphone', '').strip()
        candidates = [r for r in all_results if self.is_candidate(r.get('title', ''), r.get('url', ''), brand_core)]
        logging.info(f"Candidate product pages after pre-filter: {len(candidates)}")

        urls = [r["url"] for r in candidates if r.get("url")]
        extracted = self.extract_content(urls)

        for r in candidates:
            if r["url"] in extracted:
                r["content"] = extracted[r["url"]]

        non_candidates = [r for r in all_results if r not in candidates]
        return candidates + non_candidates