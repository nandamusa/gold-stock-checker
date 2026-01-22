from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from curl_cffi.requests import AsyncSession

from logger import log
from parser import ProductData
from config import TELEGRAM_TOKEN, CHAT_IDS


class Notifier:
    def __init__(self):
        if not TELEGRAM_TOKEN or not CHAT_IDS:
            log.warning("telegram.credentials_missing")
            self._active = False
        else:
            self._active = True
            self._url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    def _format_message(self, location_key: str, display_name: str, products: List[ProductData]) -> str:
        now = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%H:%M:%S")
        loc_header = display_name or location_key.replace("_", " ").title()
        loc_header = loc_header.replace("Antam", "Node").replace("ANTAM", "NODE")
        
        available_items = [p for p in products if "✅" in p['status']]
        header = (
            f"📍 {loc_header}\n"
            f"🕒 {now}\n"
            f"{'—' * 15}\n\n"
        )
        if not available_items:
            return header + "🔴 *ALL STOCK OUT*"
        
        items_str = "\n\n".join(
            [f"🔹 *{p['product']}*\nStatus: {p['status']}" for p in available_items]
        )
        
        return header + items_str

    async def send_stock_update(self, location_key: str, display_name: str, products: List[ProductData]):
        if not self._active or not products:
            return

        message = self._format_message(location_key, display_name, products)

        async with AsyncSession() as session:
            for chat_id in CHAT_IDS:
                payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
                
                try:
                    resp = await session.post(self._url, json=payload)
                    if resp.status_code == 200:
                        try:
                            resp_data = resp.json()
                            chat_info = resp_data.get("result", {}).get("chat", {})
                            recipient = chat_info.get("username") or chat_info.get("first_name") or chat_id
                        except Exception:
                            recipient = chat_id
                        
                        log.info("telegram.sent", location=location_key, to_user=recipient)
                    else:
                        log.error("telegram.failed", status=resp.status_code, user=chat_id)
                except Exception as e:
                    log.error("telegram.error", user=chat_id, error=str(e))