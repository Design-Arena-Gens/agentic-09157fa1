"""
Playwright-based scraper with full stealth and Kasada bypass
This should work in headless or headful mode
"""

import random
import time
import asyncio
from typing import Dict
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, Page
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
    "https://www.realestate.com.au/vic/south-yarra-3141/",
    "https://www.realestate.com.au/vic/richmond-3121/",
    "https://www.realestate.com.au/vic/carlton-3053/",
]


def simulate_human_scroll(page: Page):
    """Simulate human scrolling behavior"""
    try:
        for _ in range(random.randint(3, 7)):
            scroll_amount = random.randint(200, 600)
            page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.4, 1.2))

        # Sometimes scroll back up
        if random.random() > 0.6:
            page.evaluate(f"window.scrollBy(0, -{random.randint(150, 400)})")
            time.sleep(random.uniform(0.3, 0.8))
    except Exception as e:
        logger.debug(f"Scroll simulation failed: {e}")


def simulate_mouse_movements(page: Page):
    """Simulate random mouse movements"""
    try:
        for _ in range(random.randint(2, 6)):
            x = random.randint(100, 1000)
            y = random.randint(100, 700)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.4))
    except Exception as e:
        logger.debug(f"Mouse simulation failed: {e}")


def scrape_with_playwright_sync(session_id: int) -> Dict:
    """Scrape using synchronous Playwright"""
    result = {
        'session_id': session_id,
        'success': False,
        'url': TARGET_URL,
        'timestamp': datetime.now().isoformat(),
        'page_title': None,
        'page_text': None,
        'error': None
    }

    with sync_playwright() as p:
        try:
            # Launch browser with proxy - try headful first
            logger.info(f"Session {session_id}: Launching browser (headful)")
            try:
                browser = p.chromium.launch(
                    headless=False,
                    proxy={
                        "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
                        "username": PROXY_USER,
                        "password": PROXY_PASS
                    },
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                    ]
                )
            except Exception as headful_error:
                logger.warning(f"Session {session_id}: Headful failed, trying headless: {headful_error}")
                browser = p.chromium.launch(
                    headless=True,
                    proxy={
                        "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
                        "username": PROXY_USER,
                        "password": PROXY_PASS
                    },
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )

            # Create context with realistic settings
            context = browser.new_context(
                viewport={'width': random.randint(1366, 1920), 'height': random.randint(768, 1080)},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-AU',
                timezone_id='Australia/Melbourne',
                permissions=['geolocation'],
                geolocation={'latitude': -37.8136, 'longitude': 144.9631},  # Melbourne
                extra_http_headers={
                    'Accept-Language': 'en-AU,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                }
            )

            # Add stealth scripts
            context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Mock chrome object
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {}
                };

                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-AU', 'en-US', 'en']
                });

                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Override hardwareConcurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });

                // Override deviceMemory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
            """)

            page = context.new_page()

            # Visit decoy sites
            num_decoys = random.randint(5, 20)
            logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

            for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
                try:
                    logger.info(f"Session {session_id}: Decoy -> {url}")
                    page.goto(url, wait_until='domcontentloaded', timeout=25000)
                    time.sleep(random.uniform(2, 5))

                    # Simulate human behavior
                    simulate_human_scroll(page)
                    simulate_mouse_movements(page)
                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    logger.warning(f"Session {session_id}: Decoy visit failed: {e}")

            # Wait before visiting target
            wait_time = random.uniform(5, 10)
            logger.info(f"Session {session_id}: Waiting {wait_time:.1f}s before target")
            time.sleep(wait_time)

            # Visit target URL
            logger.info(f"Session {session_id}: Visiting target {TARGET_URL}")
            page.goto(TARGET_URL, wait_until='networkidle', timeout=60000)

            # Wait for Kasada challenge to resolve
            logger.info(f"Session {session_id}: Waiting for Kasada challenge to resolve...")
            time.sleep(random.uniform(8, 15))

            # Simulate human behavior on target page
            simulate_human_scroll(page)
            simulate_mouse_movements(page)
            time.sleep(random.uniform(3, 7))

            # Additional wait for dynamic content
            time.sleep(random.uniform(3, 6))

            # Get page content
            result['page_title'] = page.title()
            result['page_text'] = page.inner_text('body')[:5000]

            # Check for success indicators
            page_source = page.content().lower()
            page_text = result['page_text'].lower()

            if '429' in result['page_text'] or 'rate limit' in page_text:
                result['error'] = "Rate limited (429)"
                logger.error(f"Session {session_id}: Rate limited")
            elif len(result['page_text']) < 200:
                result['error'] = "Minimal content"
                logger.error(f"Session {session_id}: Minimal content ({len(result['page_text'])} chars)")
            elif 'blocked' in page_text or 'access denied' in page_text:
                result['error'] = "Access blocked"
                logger.error(f"Session {session_id}: Access blocked")
            else:
                result['success'] = True
                logger.info(f"Session {session_id}: ✓ SUCCESS! Got {len(result['page_text'])} chars")
                logger.info(f"Session {session_id}: Title: {result['page_title']}")
                logger.info(f"Session {session_id}: Preview: {result['page_text'][:500]}")

            browser.close()

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Session {session_id}: Error: {e}")

    return result


def main():
    """Main function to run scraping sessions"""
    logger.info("=" * 80)
    logger.info("PLAYWRIGHT PROXY SCRAPER - Kasada Bypass")
    logger.info(f"Target: {TARGET_URL}")
    logger.info("=" * 80)

    results = []

    # Run sessions sequentially to avoid resource issues
    for session_id in range(1, 4):
        logger.info(f"\n{'='*80}")
        logger.info(f"Starting Session {session_id}/3")
        logger.info(f"{'='*80}")

        result = scrape_with_playwright_sync(session_id)
        results.append(result)

        # Wait between sessions
        if session_id < 3:
            wait_time = random.uniform(5, 10)
            logger.info(f"Waiting {wait_time:.1f}s before next session...")
            time.sleep(wait_time)

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
        logger.info(f"  Title: {result.get('page_title', 'N/A')}")
        logger.info(f"  Error: {result.get('error', 'None')}")
        if result.get('success'):
            logger.info(f"  Content length: {len(result.get('page_text', ''))} chars")

    # Save results
    output_file = f"playwright_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")
    logger.info("=" * 80)

    return results


if __name__ == "__main__":
    main()
