import os
from typing import Final
from dotenv import load_dotenv

load_dotenv()


BASE_URL: Final[str] = os.getenv("BASE_URL")
TELEGRAM_TOKEN: Final[str] = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = [x.strip() for x in os.getenv("TELEGRAM_CHAT_ID").split(",") if x.strip()]
PROXY = os.getenv("PROXY", "").strip()

SELECTORS: Final[dict] = {
    "location": ".quick-change-location .text",
    "rows": "form#purchase .ctr",
    "row_item": ".item-1",
    "item_name": ".ngc-text",
    "out_of_stock": ".no-stock",
    "csrf_token": "input[name='_token']"
}

ENDPOINTS: Final[dict] = {
    "inventory": "/id/purchase/gold",
    "location_switch": "/id/change-location",
    "do_location_switch": "/do-change-location",
}

LOCATION_MAP: Final[dict] = {
    "pulogadung": "ABDH",
    "graha_dipta": "AGDP",
    "main_office": "AJK2",
    "setiabudi": "AJK4",
    "serpong": "ABSD",
    "bintaro": "BTR01",
    "bogor": "BGR01",
    "bekasi": "BKS01",
    "juanda": "JKT05",
    "puri_indah": "JKT06",
}