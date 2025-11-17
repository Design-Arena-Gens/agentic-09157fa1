"""
Ultimate scraper with maximum stealth - sequential slow requests
Mimics human behavior as closely as possible
"""

import random
import time
from typing import Dict
import json
from datetime import datetime
import logging

try:
    import tls_client
    HAS_TLS = True
except:
    HAS_TLS = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Proxy configuration
PROXY_USER = "c147d949a38ca89c4c3a__cr.au,gb,us"
PROXY_PASS = "b7351118825adfbd"
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT = "823"

TARGET_URL = "https://www.realestate.com.au/vic/st-kilda-3182/"

LONG_DECOY_URLS = [
    "https://www.realestate.com.au/",
    "https://www.realestate.com.au/buy/",
    "https://www.realestate.com.au/rent/",
    "https://www.realestate.com.au/sold/",
    "https://www.realestate.com.au/vic/",
    "https://www.realestate.com.au/buy/in-melbourne,+vic/list-1",
    "https://www.realestate.com.au/buy/property-house-in-melbourne,+vic/list-1",
    "https://www.realestate.com.au/vic/melbourne-3000/",
    "https://www.realestate.com.au/vic/southbank-3006/",
    "https://www.realestate.com.au/vic/carlton-3053/",
    "https://www.realestate.com.au/vic/fitzroy-3065/",
    "https://www.realestate.com.au/vic/collingwood-3066/",
    "https://www.realestate.com.au/vic/richmond-3121/",
    "https://www.realestate.com.au/vic/south-yarra-3141/",
    "https://www.realestate.com.au/vic/prahran-3181/",
    "https://www.realestate.com.au/vic/windsor-3181/",
    "https://www.realestate.com.au/vic/st-kilda-east-3183/",
    "https://www.realestate.com.au/vic/elwood-3184/",
    "https://www.realestate.com.au/vic/albert-park-3206/",
    "https://www.realestate.com.au/vic/port-melbourne-3207/",
]


def get_headers(referer=None):
    """Ultra-realistic headers"""
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'accept-encoding': 'gzip, deflate, br',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none' if not referer else 'same-origin',
        'sec-fetch-user': '?1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    if referer:
        headers['referer'] = referer

    return headers


def scrape_ultra_stealth(session_id: int) -> Dict:
    """Ultra-stealthy sequential scraping"""
    result = {
        'session_id': session_id,
        'success': False,
        'url': TARGET_URL,
        'timestamp': datetime.now().isoformat(),
        'page_text': None,
        'error': None,
        'status_code': None
    }

    if not HAS_TLS:
        result['error'] = "tls_client required"
        return result

    try:
        # Create session
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

        # Visit 5-20 decoy sites with VERY slow, human-like behavior
        num_decoys = random.randint(5, 20)
        logger.info(f"Session {session_id}: Will visit {num_decoys} sites (SLOW human-like)")

        last_url = None
        for i, url in enumerate(random.sample(LONG_DECOY_URLS, min(num_decoys, len(LONG_DECOY_URLS)))):
            try:
                logger.info(f"Session {session_id}: [{i+1}/{num_decoys}] Visiting: {url}")
                headers = get_headers(referer=last_url)
                response = session.get(url, headers=headers)
                last_url = url

                logger.info(f"Session {session_id}: [{i+1}/{num_decoys}] Status {response.status_code}, {len(response.text) if hasattr(response, 'text') else 0} chars")

                # LONG realistic wait - humans spend time reading
                read_time = random.uniform(4, 12)
                logger.info(f"Session {session_id}: [{i+1}/{num_decoys}] Reading for {read_time:.1f}s...")
                time.sleep(read_time)

            except Exception as e:
                logger.warning(f"Session {session_id}: Decoy failed {url}: {e}")
                time.sleep(random.uniform(2, 5))

        # LONG wait before target (like a human would)
        pre_target_wait = random.uniform(10, 25)
        logger.info(f"Session {session_id}: ⏰ Waiting {pre_target_wait:.1f}s before target (human pause)")
        time.sleep(pre_target_wait)

        # Finally visit target
        logger.info(f"Session {session_id}: 🎯 NOW visiting target: {TARGET_URL}")
        headers = get_headers(referer=last_url)
        response = session.get(TARGET_URL, headers=headers)

        result['status_code'] = response.status_code
        result['page_text'] = response.text[:5000] if hasattr(response, 'text') else str(response.content[:5000])

        logger.info(f"Session {session_id}: Response status={response.status_code}, size={len(result['page_text'])} chars")

        # Analyze response
        if response.status_code == 200:
            page_lower = result['page_text'].lower()

            # Check for real content
            if len(result['page_text']) > 1000:
                # Look for expected keywords
                keywords = ['st kilda', 'property', 'real estate', 'suburb', 'vic', '3182', 'house', 'home']
                found_keywords = [kw for kw in keywords if kw in page_lower]

                if found_keywords:
                    result['success'] = True
                    logger.info(f"Session {session_id}: ✓✓✓ SUCCESS! {len(result['page_text'])} chars, keywords: {found_keywords}")
                    logger.info(f"Session {session_id}: Content preview:\n{result['page_text'][:800]}")
                else:
                    result['error'] = f"{len(result['page_text'])} chars but no keywords"
                    logger.warning(f"Session {session_id}: {result['error']}")
                    logger.info(f"Session {session_id}: Content preview:\n{result['page_text'][:800]}")
            else:
                result['error'] = f"Only {len(result['page_text'])} chars"
                logger.error(f"Session {session_id}: {result['error']}")
                logger.info(f"Session {session_id}: Content:\n{result['page_text']}")
        elif response.status_code == 429:
            result['error'] = "Rate limited (429) - detected"
            logger.error(f"Session {session_id}: Still rate limited despite stealth")
        elif response.status_code == 403:
            result['error'] = "Forbidden (403) - blocked"
            logger.error(f"Session {session_id}: Blocked/Forbidden")
        else:
            result['error'] = f"HTTP {response.status_code}"
            logger.error(f"Session {session_id}: Unexpected status {response.status_code}")

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Session {session_id}: Exception: {e}")

    return result


def main():
    """Run sessions SEQUENTIALLY with maximum time between them"""
    logger.info("=" * 80)
    logger.info("ULTIMATE STEALTH SCRAPER - Maximum Human Simulation")
    logger.info(f"Target: {TARGET_URL}")
    logger.info(f"TLS-Client: {HAS_TLS}")
    logger.info("Running 3 sessions SEQUENTIALLY with long delays")
    logger.info("=" * 80)

    if not HAS_TLS:
        logger.error("❌ tls_client required! Install: pip install tls-client")
        return []

    results = []

    for i in range(1, 4):
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING SESSION {i}/3")
        logger.info(f"{'='*80}")

        result = scrape_ultra_stealth(i)
        results.append(result)

        # LONG wait between sessions to avoid detection
        if i < 3:
            between_session_wait = random.uniform(30, 60)
            logger.info(f"\n⏰ Waiting {between_session_wait:.0f}s before next session...")
            time.sleep(between_session_wait)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("FINAL RESULTS")
    logger.info("=" * 80)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    logger.info(f"✓ Successful: {len(successful)}/3")
    logger.info(f"✗ Failed: {len(failed)}/3")

    for result in results:
        logger.info(f"\nSession {result['session_id']}:")
        logger.info(f"  {'✓' if result['success'] else '✗'} Success: {result['success']}")
        logger.info(f"  Status: {result.get('status_code', 'N/A')}")
        logger.info(f"  Error: {result.get('error', 'None')}")
        if result.get('page_text'):
            logger.info(f"  Content: {len(result['page_text'])} chars")

    # Save
    output_file = f"ultimate_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✓ Saved to: {output_file}")
    logger.info("=" * 80)

    return results


if __name__ == "__main__":
    main()
