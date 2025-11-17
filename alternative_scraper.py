"""
Alternative scraping approach using Playwright with stealth plugins
This is a backup if undetected-chromedriver fails
"""

import random
import time
import asyncio
from typing import List, Dict
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Proxy configuration
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT = "823"
PROXY_USER = "c147d949a38ca89c4c3a__cr.au,gb,us"
PROXY_PASS = "b7351118825adfbd"

TARGET_URL = "https://www.realestate.com.au/vic/st-kilda-3182/"

DECOY_URLS = [
    "https://www.realestate.com.au/",
    "https://www.realestate.com.au/vic/",
    "https://www.realestate.com.au/buy",
    "https://www.realestate.com.au/rent",
    "https://www.realestate.com.au/vic/melbourne-3000/",
    "https://www.realestate.com.au/vic/south-yarra-3141/",
    "https://www.realestate.com.au/vic/richmond-3121/",
]


async def simulate_human_behavior(page: Page):
    """Simulate human-like interactions"""
    try:
        # Random mouse movements
        for _ in range(random.randint(2, 5)):
            await page.mouse.move(
                random.randint(100, 800),
                random.randint(100, 600)
            )
            await asyncio.sleep(random.uniform(0.1, 0.3))

        # Scroll
        for _ in range(random.randint(3, 7)):
            await page.evaluate(f"window.scrollBy(0, {random.randint(100, 400)})")
            await asyncio.sleep(random.uniform(0.3, 0.8))

        # Random delays
        await asyncio.sleep(random.uniform(2, 5))

    except Exception as e:
        logger.debug(f"Behavior simulation error: {e}")


async def scrape_with_playwright(session_id: int) -> Dict:
    """Scrape using Playwright"""
    result = {
        'session_id': session_id,
        'success': False,
        'url': TARGET_URL,
        'timestamp': datetime.now().isoformat(),
        'page_title': None,
        'page_text': None,
        'error': None
    }

    async with async_playwright() as p:
        try:
            # Launch browser with proxy
            browser = await p.chromium.launch(
                headless=False,  # Headful for Kasada
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

            context = await browser.new_context(
                viewport={'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Add stealth scripts
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                window.chrome = {
                    runtime: {}
                };

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)

            page = await context.new_page()

            # Visit decoy sites
            num_decoys = random.randint(5, 20)
            logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

            for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(random.uniform(2, 5))
                    await simulate_human_behavior(page)
                except Exception as e:
                    logger.warning(f"Session {session_id}: Decoy visit failed: {e}")

            # Visit target
            logger.info(f"Session {session_id}: Visiting target {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=60000)

            # Wait for Kasada challenge to resolve
            await asyncio.sleep(random.uniform(5, 10))

            # Simulate human behavior
            await simulate_human_behavior(page)

            # Additional wait
            await asyncio.sleep(random.uniform(3, 6))

            # Get content
            result['page_title'] = await page.title()
            result['page_text'] = (await page.inner_text('body'))[:5000]

            if result['page_text'] and len(result['page_text']) > 100:
                result['success'] = True
                logger.info(f"Session {session_id}: SUCCESS! Got {len(result['page_text'])} chars")
            else:
                result['error'] = "Empty or minimal content"
                logger.error(f"Session {session_id}: Failed - minimal content")

            await browser.close()

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Session {session_id}: Error: {e}")

    return result


async def run_parallel_playwright_sessions(num_sessions: int = 3):
    """Run multiple Playwright sessions"""
    tasks = [scrape_with_playwright(i+1) for i in range(num_sessions)]
    results = await asyncio.gather(*tasks)
    return results


def main_playwright():
    """Main function for Playwright scraper"""
    logger.info("Starting Playwright-based scraper")
    results = asyncio.run(run_parallel_playwright_sessions(3))

    # Summary
    successful = [r for r in results if r.get('success')]
    logger.info(f"Success rate: {len(successful)}/{len(results)}")

    for result in results:
        logger.info(f"Session {result['session_id']}: {result['success']}")
        if result.get('success'):
            logger.info(f"  Title: {result['page_title']}")
            logger.info(f"  Content preview: {result['page_text'][:200]}")

    return results


if __name__ == "__main__":
    main_playwright()
