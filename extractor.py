from urllib.parse import unquote
from curl_cffi.requests import AsyncSession

from config import BASE_URL
from exceptions import LoginError, LocationChangeError
from parser import Parser
from logger import log


class Extractor:
    def __init__(self):
        self._session = AsyncSession(impersonate="chrome")

    async def close(self):
        """Cleanup resources."""
        if hasattr(self._session, 'close'):
             await self._session.close()

    async def process_location(self, loc_name: str, loc_id: str) -> dict:
        log.info("extractor.start", location=loc_name)

        # 1. Get Initial Page for CSRF
        try:
            resp_init = await self._session.get(f"{BASE_URL}/id/purchase/gold")
            if resp_init.status_code != 200:
                raise LoginError(f"Init page failed: {resp_init.status_code}")
        except Exception as e:
            raise LoginError(f"Connection failed: {e}")

        init_parser = Parser(resp_init.text)
        csrf_token = init_parser.get_csrf_token()

        # 2. Get XSRF Cookie
        await self._session.get(f"{BASE_URL}/id/change-location")
        
        xsrf_cookie = self._session.cookies.get("XSRF-TOKEN")
        if not xsrf_cookie:
            raise LoginError("XSRF-TOKEN cookie missing")

        # 3. Post Location Change
        headers = {
            "X-XSRF-TOKEN": unquote(xsrf_cookie),
            "Referer": f"{BASE_URL}/id/purchase/gold",
            "Origin": BASE_URL,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        payload = {"_token": csrf_token, "location": loc_id}

        try:
            resp_change = await self._session.post(
                f"{BASE_URL}/do-change-location", 
                data=payload, 
                headers=headers
            )
        except Exception as e:
            raise LocationChangeError(f"POST request failed: {e}")

        # 4. Verify & Parse Result
        # We check if we landed on the correct URL OR if we got a success 200 OK
        # (302 check is removed because the client likely already handled it)
        is_correct_url = "purchase/gold" in resp_change.url
        is_success_code = resp_change.status_code == 200

        if is_correct_url and is_success_code:
            final_parser = Parser(resp_change.text)
            display_name, products = final_parser.parse_stock_data()
            
            log.info("extractor.success", location=loc_name, items_found=len(products))
            return {
                "key": loc_name, 
                "display_name": display_name, 
                "products": products
            }
        else:
            raise LocationChangeError(f"Location switch failed. Ended at: {resp_change.url}")