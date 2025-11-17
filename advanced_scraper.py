"""
Advanced scraper using requests-html with JavaScript rendering
and aggressive stealth techniques
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import json
from datetime import datetime
from requests_html import HTMLSession, AsyncHTMLSession
import asyncio
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
    "https://www.realestate.com.au/vic/melbourne-3000/",
]


def get_advanced_headers():
    """Generate comprehensive browser headers"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]

    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,en-AU;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }


async def scrape_async_with_rendering(session_id: int) -> Dict:
    """Async scraper with JavaScript rendering"""
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
    proxies = {'http': proxy_url, 'https': proxy_url}

    try:
        asession = AsyncHTMLSession()

        # Visit decoy sites
        num_decoys = random.randint(5, 20)
        logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

        for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
            try:
                r = await asession.get(url, proxies=proxies, headers=get_advanced_headers(), timeout=20)
                await asyncio.sleep(random.uniform(1.5, 4.0))
            except Exception as e:
                logger.debug(f"Session {session_id}: Decoy failed: {e}")

        # Wait before target
        await asyncio.sleep(random.uniform(4, 9))

        # Visit target with JavaScript rendering
        logger.info(f"Session {session_id}: Scraping target with JS rendering")
        r = await asession.get(TARGET_URL, proxies=proxies, headers=get_advanced_headers(), timeout=60)

        # Render JavaScript (this is key for Kasada)
        await r.html.arender(timeout=30, sleep=5, keep_page=True, scrolldown=3)

        result['status_code'] = r.status_code
        result['page_text'] = r.html.text[:5000]

        if r.status_code == 200 and len(r.html.text) > 200:
            result['success'] = True
            logger.info(f"Session {session_id}: SUCCESS! Got {len(r.html.text)} chars")
            logger.info(f"Session {session_id}: Preview: {r.html.text[:400]}")
        else:
            result['error'] = f"Status {r.status_code} or minimal content"
            logger.error(f"Session {session_id}: Failed - {result['error']}")

        await asession.close()

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Session {session_id}: Error: {e}")

    return result


async def run_async_sessions(num_sessions: int = 3):
    """Run multiple async sessions"""
    tasks = [scrape_async_with_rendering(i+1) for i in range(num_sessions)]
    results = await asyncio.gather(*tasks)
    return results


def main_async():
    """Main function for async scraper"""
    logger.info("Starting async scraper with JavaScript rendering")
    results = asyncio.run(run_async_sessions(3))

    # Summary
    successful = [r for r in results if r.get('success')]
    logger.info(f"Success rate: {len(successful)}/{len(results)}")

    for result in results:
        logger.info(f"Session {result['session_id']}: {result['success']} (Status: {result['status_code']})")
        if result.get('success'):
            logger.info(f"  Preview: {result['page_text'][:300]}")

    return results


if __name__ == "__main__":
    main_async()
