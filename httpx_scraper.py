"""
HTTPX-based scraper with HTTP/2 support and advanced fingerprinting
Uses httpx with custom TLS and HTTP/2 configuration
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
import json
from datetime import datetime
import httpx
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
    "https://www.realestate.com.au/rent",
    "https://www.realestate.com.au/sold",
    "https://www.realestate.com.au/vic/melbourne-3000/",
    "https://www.realestate.com.au/vic/south-yarra-3141/",
    "https://www.realestate.com.au/vic/richmond-3121/",
]


def get_realistic_headers(referer=None):
    """Generate very realistic browser headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-AU,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none' if not referer else 'same-origin',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cache-Control': 'max-age=0',
    }

    if referer:
        headers['Referer'] = referer
        headers['Sec-Fetch-Site'] = 'same-origin'

    return headers


def scrape_with_httpx(session_id: int) -> Dict:
    """Scrape using httpx with HTTP/2"""
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

    try:
        # Create client with HTTP/2 support
        with httpx.Client(
            http2=True,
            proxy=proxy_url,
            timeout=httpx.Timeout(60.0, connect=30.0),
            follow_redirects=True,
            verify=False,  # Sometimes necessary for proxy
        ) as client:

            # Visit decoy sites
            num_decoys = random.randint(5, 20)
            logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

            last_url = None
            for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
                try:
                    headers = get_realistic_headers(referer=last_url)
                    response = client.get(url, headers=headers)
                    last_url = url

                    # Simulate reading time
                    time.sleep(random.uniform(2, 5))

                    logger.debug(f"Session {session_id}: Decoy {url} -> {response.status_code}")

                except Exception as e:
                    logger.warning(f"Session {session_id}: Decoy failed: {e}")

            # Wait before target with realistic delay
            wait_time = random.uniform(5, 12)
            logger.info(f"Session {session_id}: Waiting {wait_time:.1f}s before target")
            time.sleep(wait_time)

            # Visit target URL
            logger.info(f"Session {session_id}: Scraping target {TARGET_URL}")
            headers = get_realistic_headers(referer=last_url)

            response = client.get(TARGET_URL, headers=headers)

            result['status_code'] = response.status_code
            result['page_text'] = response.text[:5000]

            # Check for success
            if response.status_code == 200:
                if len(response.text) > 500:
                    # Check for actual content
                    text_lower = response.text.lower()

                    if 'st kilda' in text_lower or 'property' in text_lower or 'real estate' in text_lower:
                        result['success'] = True
                        logger.info(f"Session {session_id}: ✓ SUCCESS! Got {len(response.text)} chars")
                        logger.info(f"Session {session_id}: Preview: {response.text[:600]}")
                    else:
                        result['error'] = f"Got {len(response.text)} chars but no expected content"
                        logger.warning(f"Session {session_id}: {result['error']}")
                        logger.info(f"Session {session_id}: Preview: {response.text[:600]}")
                else:
                    result['error'] = f"Minimal content ({len(response.text)} chars)"
                    logger.error(f"Session {session_id}: {result['error']}")
            elif response.status_code == 429:
                result['error'] = "Rate limited (429)"
                logger.error(f"Session {session_id}: Rate limited")
            elif response.status_code == 403:
                result['error'] = "Forbidden (403) - likely detected"
                logger.error(f"Session {session_id}: Forbidden")
            else:
                result['error'] = f"HTTP {response.status_code}"
                logger.error(f"Session {session_id}: HTTP {response.status_code}")

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Session {session_id}: Error: {e}")

    return result


def run_httpx_parallel(num_sessions: int = 3):
    """Run multiple httpx sessions in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [executor.submit(scrape_with_httpx, i+1) for i in range(num_sessions)]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("HTTPX HTTP/2 SCRAPER - Kasada Bypass Attempt")
    logger.info(f"Target: {TARGET_URL}")
    logger.info("=" * 80)

    results = run_httpx_parallel(3)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SCRAPING SUMMARY")
    logger.info("=" * 80)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    logger.info(f"Total sessions: {len(results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")

    for result in results:
        logger.info(f"\nSession {result['session_id']}:")
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Status: {result.get('status_code', 'N/A')}")
        logger.info(f"  Error: {result.get('error', 'None')}")
        if result.get('page_text'):
            logger.info(f"  Content length: {len(result['page_text'])} chars")

    # Save results
    output_file = f"httpx_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")
    logger.info("=" * 80)

    return results


if __name__ == "__main__":
    main()
