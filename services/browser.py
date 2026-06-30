import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class LinkedInBrowserService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False

    async def start_browser(self, headless: bool = True):
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=headless)
            context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self.page = await context.new_page()
            logger.info("Browser started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    async def stop_browser(self):
        if self.browser:
            await self.browser.close()
            logger.info("Browser stopped")

    async def login_with_cookies(self, cookies: List[Dict]) -> bool:
        try:
            if not self.page:
                return False
            await self.page.goto("https://www.linkedin.com")
            await self.page.context.add_cookies(cookies)
            await self.page.reload()
            await asyncio.sleep(2)
            self.is_logged_in = True
            logger.info("Logged in successfully with cookies")
            return True
        except Exception as e:
            logger.error(f"Failed to log in: {e}")
            return False

    async def search_profiles(
        self,
        keywords: Optional[str] = None,
        company: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
        industry: Optional[str] = None,
        university: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        profiles = []
        try:
            search_url = "https://www.linkedin.com/search/results/people/"
            params = []
            if keywords:
                params.append(f"keywords={keywords}")
            if company:
                params.append(f"company={company}")
            if role:
                params.append(f"title={role}")
            if location:
                params.append(f"location={location}")
            if industry:
                params.append(f"industry={industry}")
            if university:
                params.append(f"school={university}")
            
            full_url = f"{search_url}?{'&'.join(params)}" if params else search_url
            
            await self.page.goto(full_url)
            await asyncio.sleep(3)
            
            profile_cards = await self.page.query_selector_all("li.reusable-search__result-container")
            
            for card in profile_cards[:max_results]:
                try:
                    profile = await self._extract_profile_data(card)
                    if profile:
                        profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Failed to extract profile: {e}")
                    continue
            
            logger.info(f"Found {len(profiles)} profiles")
            return profiles
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return profiles

    async def _extract_profile_data(self, card) -> Optional[Dict]:
        try:
            name_elem = await card.query_selector(".entity-result__title-text a span")
            name = await name_elem.inner_text() if name_elem else None
            
            url_elem = await card.query_selector(".entity-result__title-text a")
            profile_url = await url_elem.get_attribute("href") if url_elem else None
            if profile_url:
                profile_url = f"https://www.linkedin.com{profile_url.split('?')[0]}"
            
            title_elem = await card.query_selector(".entity-result__primary-subtitle")
            title = await title_elem.inner_text() if title_elem else None
            
            location_elem = await card.query_selector(".entity-result__secondary-subtitle")
            location = await location_elem.inner_text() if location_elem else None
            
            if name and profile_url:
                return {
                    "name": name,
                    "profile_url": profile_url,
                    "title": title,
                    "location": location
                }
            return None
        except Exception as e:
            logger.debug(f"Extraction failed: {e}")
            return None

    async def send_connection_request(
        self, profile_url: str, message: Optional[str] = None
    ) -> bool:
        try:
            await self.page.goto(profile_url)
            await asyncio.sleep(2)
            
            # Try to find connect button
            connect_button = None
            selectors = [
                "button[aria-label*='Connect']",
                "button[data-control-name='connect']",
                ".artdeco-button--primary"
            ]
            
            for selector in selectors:
                try:
                    connect_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if connect_button:
                        break
                except PlaywrightTimeoutError:
                    continue
            
            if not connect_button:
                logger.warning("Connect button not found")
                return False
            
            await connect_button.click()
            await asyncio.sleep(1)
            
            if message:
                try:
                    message_input = await self.page.wait_for_selector("textarea#custom-message", timeout=3000)
                    if message_input:
                        await message_input.fill(message)
                        await asyncio.sleep(0.5)
                except PlaywrightTimeoutError:
                    logger.debug("Message input not found, proceeding without message")
            
            # Send the request
            send_button = await self.page.wait_for_selector("button[aria-label*='Send now'], button.artdeco-button--primary", timeout=3000)
            if send_button:
                await send_button.click()
                await asyncio.sleep(1)
                logger.info(f"Connection request sent to {profile_url}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to send connection request: {e}")
            return False


_browser_service_instance: Optional[LinkedInBrowserService] = None


def get_browser_service() -> LinkedInBrowserService:
    global _browser_service_instance
    if not _browser_service_instance:
        _browser_service_instance = LinkedInBrowserService()
    return _browser_service_instance

