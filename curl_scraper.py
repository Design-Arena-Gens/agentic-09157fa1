"""
Lightweight curl-based approach with TLS fingerprint spoofing
Uses curl_cffi which mimics browser TLS fingerprints
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
import json
from datetime import datetime
from curl_cffi import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Proxy configuration
PROXY_USER = "c147d949a38ca89c4c3a__cr.au,gb,us"
PROXY_PASS = "b7351118825adfbd"
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT = "823"

TARGET_URL = "https://www.realestate.com.au/vic/st-kilda-3182/"

DECOY_URLS = [
    "https://www.realestate.com.au/",
    "https://www.realestate.com.au/vic/",
    "https://www.realestate.com.au/buy",
]


def get_random_headers():
    """Generate realistic browser headers"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }


def scrape_with_curl_cffi(session_id: int) -> Dict:
    """Scrape using curl_cffi with browser impersonation"""
    result = {
        'session_id': session_id,
        'success': False,
        'url': TARGET_URL,
        'timestamp': datetime.now().isoformat(),
        'page_text': None,
        'error': None,
        'status_code': None
    }

    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    try:
        # Create session with browser impersonation
        session = requests.Session()

        # Visit decoy sites
        num_decoys = random.randint(5, 20)
        logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

        for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
            try:
                response = session.get(
                    url,
                    proxies=proxies,
                    headers=get_random_headers(),
                    timeout=30,
                    impersonate="chrome120",  # Mimic Chrome 120 TLS fingerprint
                    allow_redirects=True
                )
                time.sleep(random.uniform(2, 5))
            except Exception as e:
                logger.warning(f"Session {session_id}: Decoy failed: {e}")

        # Wait before target
        time.sleep(random.uniform(3, 7))

        # Visit target
        logger.info(f"Session {session_id}: Scraping target {TARGET_URL}")
        response = session.get(
            TARGET_URL,
            proxies=proxies,
            headers=get_random_headers(),
            timeout=60,
            impersonate="chrome120",
            allow_redirects=True
        )

        result['status_code'] = response.status_code
        result['page_text'] = response.text[:5000]

        if response.status_code == 200 and len(response.text) > 100:
            result['success'] = True
            logger.info(f"Session {session_id}: SUCCESS! Got {len(response.text)} chars")
            logger.info(f"Session {session_id}: Preview: {response.text[:300]}")
        else:
            result['error'] = f"Status {response.status_code} or minimal content"
            logger.error(f"Session {session_id}: Failed - {result['error']}")

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Session {session_id}: Error: {e}")

    return result


def run_curl_parallel_sessions(num_sessions: int = 3):
    """Run multiple curl_cffi sessions in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [executor.submit(scrape_with_curl_cffi, i+1) for i in range(num_sessions)]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def main_curl():
    """Main function for curl_cffi scraper"""
    logger.info("Starting curl_cffi-based scraper")
    results = run_curl_parallel_sessions(3)

    # Summary
    successful = [r for r in results if r.get('success')]
    logger.info(f"Success rate: {len(successful)}/{len(results)}")

    for result in results:
        logger.info(f"Session {result['session_id']}: {result['success']} (Status: {result['status_code']})")

    return results


if __name__ == "__main__":
    main_curl()
