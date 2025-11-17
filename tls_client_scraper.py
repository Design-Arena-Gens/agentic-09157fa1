"""
TLS-Client based scraper - mimics browser TLS fingerprints perfectly
This library is specifically designed to bypass Kasada/Akamai/Cloudflare
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
import json
from datetime import datetime
import logging

try:
    import tls_client
    HAS_TLS_CLIENT = True
except ImportError:
    HAS_TLS_CLIENT = False
    print("tls_client not available, trying alternative...")

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
    "https://www.realestate.com.au/vic/carlton-3053/",
]


def get_browser_headers(referer=None):
    """Get realistic browser headers"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-AU,en-US;q=0.9,en;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none' if not referer else 'same-origin',
        'sec-fetch-user': '?1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'cache-control': 'max-age=0',
    }

    if referer:
        headers['referer'] = referer

    return headers


def scrape_with_tls_client(session_id: int) -> Dict:
    """Scrape using tls_client with Chrome 120 fingerprint"""
    result = {
        'session_id': session_id,
        'success': False,
        'url': TARGET_URL,
        'timestamp': datetime.now().isoformat(),
        'page_text': None,
        'error': None,
        'status_code': None
    }

    if not HAS_TLS_CLIENT:
        result['error'] = "tls_client not available"
        return result

    try:
        # Create session with Chrome 120 JA3 fingerprint
        session = tls_client.Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True
        )

        # Set proxy
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        # Visit decoy sites to build session history
        num_decoys = random.randint(5, 20)
        logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

        last_url = None
        for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
            try:
                headers = get_browser_headers(referer=last_url)
                response = session.get(url, headers=headers)
                last_url = url

                # Simulate human reading time
                time.sleep(random.uniform(2.5, 6.0))

                logger.debug(f"Session {session_id}: Decoy {url} -> {response.status_code}")

            except Exception as e:
                logger.warning(f"Session {session_id}: Decoy failed {url}: {e}")

        # Wait before targeting the actual page
        wait_time = random.uniform(6, 14)
        logger.info(f"Session {session_id}: Waiting {wait_time:.1f}s before target")
        time.sleep(wait_time)

        # Visit target URL with realistic headers
        logger.info(f"Session {session_id}: Scraping target {TARGET_URL}")
        headers = get_browser_headers(referer=last_url)

        response = session.get(TARGET_URL, headers=headers)

        result['status_code'] = response.status_code
        result['page_text'] = response.text[:5000] if hasattr(response, 'text') else str(response.content[:5000])

        # Analyze response
        if response.status_code == 200:
            page_text = result['page_text'].lower()

            # Check for actual content
            if len(result['page_text']) > 1000:
                # Look for expected content
                if any(keyword in page_text for keyword in ['st kilda', 'property', 'real estate', 'suburb', 'vic', '3182']):
                    result['success'] = True
                    logger.info(f"Session {session_id}: ✓✓✓ SUCCESS! Got {len(result['page_text'])} chars with real content")
                    logger.info(f"Session {session_id}: First 600 chars:\n{result['page_text'][:600]}")
                else:
                    result['error'] = f"Got {len(result['page_text'])} chars but no expected keywords"
                    logger.warning(f"Session {session_id}: {result['error']}")
                    logger.info(f"Session {session_id}: Preview:\n{result['page_text'][:600]}")
            elif len(result['page_text']) > 200:
                result['error'] = f"Partial content ({len(result['page_text'])} chars)"
                logger.warning(f"Session {session_id}: {result['error']}")
                logger.info(f"Session {session_id}: Preview:\n{result['page_text'][:600]}")
            else:
                result['error'] = f"Minimal content ({len(result['page_text'])} chars)"
                logger.error(f"Session {session_id}: {result['error']}")

        elif response.status_code == 429:
            result['error'] = "Rate limited (429)"
            logger.error(f"Session {session_id}: Rate limited")
        elif response.status_code == 403:
            result['error'] = "Forbidden (403)"
            logger.error(f"Session {session_id}: Forbidden - detected as bot")
        else:
            result['error'] = f"HTTP {response.status_code}"
            logger.error(f"Session {session_id}: HTTP {response.status_code}")

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Session {session_id}: Exception: {e}")

    return result


def run_tls_parallel(num_sessions: int = 3):
    """Run multiple tls_client sessions in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [executor.submit(scrape_with_tls_client, i+1) for i in range(num_sessions)]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("TLS-CLIENT SCRAPER - Advanced Fingerprint Spoofing")
    logger.info(f"Target: {TARGET_URL}")
    logger.info(f"TLS-Client available: {HAS_TLS_CLIENT}")
    logger.info("=" * 80)

    if not HAS_TLS_CLIENT:
        logger.error("tls_client library not available. Install with: pip install tls-client")
        return []

    results = run_tls_parallel(3)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SCRAPING SUMMARY")
    logger.info("=" * 80)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    logger.info(f"Total sessions: {len(results)}")
    logger.info(f"✓ Successful: {len(successful)}")
    logger.info(f"✗ Failed: {len(failed)}")

    for result in results:
        logger.info(f"\nSession {result['session_id']}:")
        logger.info(f"  Success: {'✓' if result['success'] else '✗'}")
        logger.info(f"  Status: {result.get('status_code', 'N/A')}")
        logger.info(f"  Error: {result.get('error', 'None')}")
        if result.get('page_text'):
            logger.info(f"  Content length: {len(result['page_text'])} chars")

    # Save results
    output_file = f"tls_client_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✓ Results saved to: {output_file}")
    logger.info("=" * 80)

    return results


if __name__ == "__main__":
    main()
