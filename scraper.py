import random
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import json
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# from seleniumwire import webdriver as wire_webdriver  # Not needed
from fake_useragent import UserAgent
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Proxy configuration
PROXY_HOST = "gw.dataimpulse.com"
PROXY_PORT = "823"
PROXY_USER = "c147d949a38ca89c4c3a__cr.au,gb,us"
PROXY_PASS = "b7351118825adfbd"

# Target URL
TARGET_URL = "https://www.realestate.com.au/vic/st-kilda-3182/"

# Decoy URLs for realistic browsing patterns
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
    "https://www.realestate.com.au/vic/fitzroy-3065/",
    "https://www.realestate.com.au/vic/prahran-3181/",
    "https://www.realestate.com.au/vic/collingwood-3066/",
    "https://www.realestate.com.au/vic/port-melbourne-3207/",
    "https://www.realestate.com.au/vic/brunswick-3056/",
    "https://www.realestate.com.au/vic/elwood-3184/",
    "https://www.realestate.com.au/vic/st-kilda-east-3183/",
    "https://www.realestate.com.au/vic/windsor-3181/",
    "https://www.realestate.com.au/vic/albert-park-3206/",
    "https://www.realestate.com.au/vic/kew-3101/",
    "https://www.realestate.com.au/vic/hawthorn-3122/",
]


class HumanBehaviorSimulator:
    """Simulates human-like behavior to avoid detection"""

    @staticmethod
    def random_sleep(min_sec=1, max_sec=5):
        """Random sleep with human-like timing"""
        time.sleep(random.uniform(min_sec, max_sec))

    @staticmethod
    def simulate_mouse_movement(driver):
        """Simulate random mouse movements"""
        try:
            action = ActionChains(driver)
            for _ in range(random.randint(3, 8)):
                x_offset = random.randint(-200, 200)
                y_offset = random.randint(-200, 200)
                action.move_by_offset(x_offset, y_offset)
            action.perform()
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed: {e}")

    @staticmethod
    def simulate_scrolling(driver):
        """Simulate human-like scrolling"""
        try:
            scroll_pause = random.uniform(0.5, 2.0)
            current_position = 0
            target_position = random.randint(500, 2000)

            while current_position < target_position:
                scroll_amount = random.randint(100, 300)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                current_position += scroll_amount
                time.sleep(random.uniform(0.2, 0.8))

            # Sometimes scroll back up
            if random.random() > 0.5:
                driver.execute_script(f"window.scrollBy(0, -{random.randint(200, 500)});")
                time.sleep(scroll_pause)
        except Exception as e:
            logger.debug(f"Scrolling simulation failed: {e}")

    @staticmethod
    def simulate_reading(min_sec=3, max_sec=10):
        """Simulate reading time"""
        time.sleep(random.uniform(min_sec, max_sec))


class StealthBrowser:
    """Stealth browser with anti-detection features"""

    def __init__(self, session_id: int):
        self.session_id = session_id
        self.driver = None
        self.ua = UserAgent()

    def create_driver(self) -> uc.Chrome:
        """Create an undetected Chrome driver with proxy"""
        try:
            options = uc.ChromeOptions()

            # Proxy configuration
            proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
            options.add_argument(f'--proxy-server={proxy_url}')

            # Anti-detection options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument(f'--user-agent={self.ua.random}')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')

            # Use headful mode (required for Kasada)
            options.headless = False

            # Additional stealth options
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--start-maximized')

            # Random window size
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f'--window-size={width},{height}')

            # Create driver
            driver = uc.Chrome(options=options, version_main=None)

            # Additional stealth JavaScript
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.ua.random
            })

            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en', 'en-AU']
                });

                window.chrome = {
                    runtime: {}
                };

                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
            """)

            self.driver = driver
            return driver

        except Exception as e:
            logger.error(f"Failed to create driver for session {self.session_id}: {e}")
            raise

    def visit_decoy_sites(self, num_sites: int):
        """Visit random decoy sites to build browsing history"""
        selected_sites = random.sample(DECOY_URLS, min(num_sites, len(DECOY_URLS)))

        for i, url in enumerate(selected_sites):
            try:
                logger.info(f"Session {self.session_id}: Visiting decoy {i+1}/{num_sites}: {url}")
                self.driver.get(url)

                # Wait for page load
                time.sleep(random.uniform(2, 5))

                # Simulate human behavior
                HumanBehaviorSimulator.simulate_scrolling(self.driver)
                HumanBehaviorSimulator.simulate_mouse_movement(self.driver)
                HumanBehaviorSimulator.random_sleep(2, 6)

            except Exception as e:
                logger.warning(f"Session {self.session_id}: Failed to visit decoy {url}: {e}")
                continue

    def scrape_target(self) -> Dict:
        """Scrape the target URL"""
        result = {
            'session_id': self.session_id,
            'success': False,
            'url': TARGET_URL,
            'timestamp': datetime.now().isoformat(),
            'page_title': None,
            'page_text': None,
            'error': None,
            'response_code': None
        }

        try:
            logger.info(f"Session {self.session_id}: Navigating to target: {TARGET_URL}")
            self.driver.get(TARGET_URL)

            # Wait for initial page load
            time.sleep(random.uniform(3, 7))

            # Check for Kasada challenge
            page_source = self.driver.page_source.lower()
            if 'challenge' in page_source or 'verify' in page_source:
                logger.warning(f"Session {self.session_id}: Kasada challenge detected, waiting...")
                time.sleep(random.uniform(10, 15))

            # Simulate human reading behavior
            HumanBehaviorSimulator.simulate_scrolling(self.driver)
            HumanBehaviorSimulator.simulate_reading(5, 10)
            HumanBehaviorSimulator.simulate_mouse_movement(self.driver)

            # Additional wait for dynamic content
            time.sleep(random.uniform(3, 6))

            # Try to wait for specific elements
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                logger.warning(f"Session {self.session_id}: Timeout waiting for body: {e}")

            # Get page title
            result['page_title'] = self.driver.title

            # Get page text
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            result['page_text'] = page_text[:5000]  # First 5000 chars

            # Check for common error indicators
            if not page_text or len(page_text) < 100:
                result['error'] = "Empty or minimal page content"
                logger.error(f"Session {self.session_id}: Empty or minimal content received")
            elif '429' in page_text or 'rate limit' in page_text.lower():
                result['error'] = "Rate limited (429)"
                logger.error(f"Session {self.session_id}: Rate limited")
            elif 'access denied' in page_text.lower() or 'blocked' in page_text.lower():
                result['error'] = "Access denied/blocked"
                logger.error(f"Session {self.session_id}: Access denied")
            else:
                result['success'] = True
                logger.info(f"Session {self.session_id}: Successfully scraped! Got {len(page_text)} chars")
                logger.info(f"Session {self.session_id}: Title: {result['page_title']}")
                logger.info(f"Session {self.session_id}: First 500 chars: {page_text[:500]}")

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Session {self.session_id}: Error scraping target: {e}")

        return result

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Session {self.session_id}: Error closing driver: {e}")


def run_scraping_session(session_id: int) -> Dict:
    """Run a complete scraping session"""
    logger.info(f"=== Starting Session {session_id} ===")

    browser = StealthBrowser(session_id)

    try:
        # Create browser
        browser.create_driver()

        # Visit random number of decoy sites (5-20)
        num_decoys = random.randint(5, 20)
        logger.info(f"Session {session_id}: Will visit {num_decoys} decoy sites")
        browser.visit_decoy_sites(num_decoys)

        # Random wait before target
        HumanBehaviorSimulator.random_sleep(3, 8)

        # Scrape target
        result = browser.scrape_target()

        # Random wait before closing
        HumanBehaviorSimulator.random_sleep(2, 5)

        return result

    except Exception as e:
        logger.error(f"Session {session_id}: Fatal error: {e}")
        return {
            'session_id': session_id,
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
    finally:
        browser.close()
        logger.info(f"=== Finished Session {session_id} ===")


def run_parallel_sessions(num_sessions: int = 3):
    """Run multiple scraping sessions in parallel"""
    logger.info(f"Starting {num_sessions} parallel scraping sessions")

    results = []
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = [
            executor.submit(run_scraping_session, i+1)
            for i in range(num_sessions)
        ]

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Session failed with exception: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

    return results


def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("PROXY SCRAPER - Kasada Bypass Attempt")
    logger.info(f"Target: {TARGET_URL}")
    logger.info(f"Proxy: {PROXY_HOST}:{PROXY_PORT}")
    logger.info("=" * 80)

    # Run 3 concurrent sessions
    results = run_parallel_sessions(num_sessions=3)

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
        logger.info(f"\nSession {result.get('session_id', 'N/A')}:")
        logger.info(f"  Success: {result.get('success')}")
        logger.info(f"  Title: {result.get('page_title', 'N/A')}")
        logger.info(f"  Error: {result.get('error', 'None')}")
        if result.get('success') and result.get('page_text'):
            logger.info(f"  Content length: {len(result.get('page_text', ''))} chars")

    # Save results to file
    output_file = f"scraping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")
    logger.info("=" * 80)

    return successful, failed


if __name__ == "__main__":
    main()
