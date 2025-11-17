"""
Simple Selenium-based scraper with proxy support
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
]


def create_selenium_driver():
    """Create a basic Selenium driver with proxy"""
    options = Options()

    # Proxy setup
    options.add_argument(f'--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}')

    # Stealth options
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Random window size
    width = random.randint(1200, 1920)
    height = random.randint(800, 1080)
    options.add_argument(f'--window-size={width},{height}')

    # Additional options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')

    # User agent
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)

    # Inject stealth JavaScript
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            window.chrome = { runtime: {} };
        '''
    })

    return driver


def scrape_with_selenium(session_id: int) -> Dict:
    """Scrape using basic Selenium"""
    result = {
        'session_id': session_id,
        'success': False,
        'url': TARGET_URL,
        'page_text': None,
        'error': None
    }

    driver = None
    try:
        logger.info(f"Session {session_id}: Creating driver")
        driver = create_selenium_driver()

        # Visit decoy sites
        num_decoys = random.randint(5, 20)
        logger.info(f"Session {session_id}: Visiting {num_decoys} decoy sites")

        for url in random.sample(DECOY_URLS, min(num_decoys, len(DECOY_URLS))):
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 5))

                # Scroll
                driver.execute_script(f"window.scrollBy(0, {random.randint(300, 800)})")
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                logger.debug(f"Session {session_id}: Decoy visit failed: {e}")

        # Wait before target
        time.sleep(random.uniform(4, 8))

        # Visit target
        logger.info(f"Session {session_id}: Visiting target")
        driver.get(TARGET_URL)

        # Wait for page load
        time.sleep(random.uniform(5, 10))

        # Scroll to trigger lazy loading
        for _ in range(5):
            driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)})")
            time.sleep(random.uniform(0.5, 1.5))

        # Wait for dynamic content
        time.sleep(random.uniform(5, 10))

        # Get page content
        page_text = driver.find_element(By.TAG_NAME, "body").text
        result['page_text'] = page_text[:5000]

        if page_text and len(page_text) > 200:
            result['success'] = True
            logger.info(f"Session {session_id}: SUCCESS! Got {len(page_text)} chars")
            logger.info(f"Session {session_id}: Preview: {page_text[:400]}")
        else:
            result['error'] = "Minimal or no content"
            logger.error(f"Session {session_id}: Failed - minimal content")

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Session {session_id}: Error: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    return result


def run_selenium_parallel(num_sessions: int = 3):
    """Run multiple Selenium sessions in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [executor.submit(scrape_with_selenium, i+1) for i in range(num_sessions)]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def main():
    """Main function"""
    logger.info("Starting basic Selenium scraper")
    results = run_selenium_parallel(3)

    # Summary
    successful = [r for r in results if r.get('success')]
    logger.info(f"Success rate: {len(successful)}/{len(results)}")

    for result in results:
        logger.info(f"Session {result['session_id']}: {result['success']}")
        if result.get('success'):
            logger.info(f"  Got {len(result['page_text'])} chars")

    return results


if __name__ == "__main__":
    main()
