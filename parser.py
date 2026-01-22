from typing import List, Optional, Tuple, TypedDict
from selectolax.lexbor import LexborHTMLParser, LexborNode
import json
import re

from config import SELECTORS
from exceptions import ParseError
from logger import log


class ProductData(TypedDict):
    product: str
    status: str
    quantity: int

class Parser:
    def __init__(self, html: str):
        if not html:
            raise ParseError("Cannot parse empty HTML")
        self._html = html
        self._parser = LexborHTMLParser(html)

    def get_csrf_token(self) -> str:
        node = self._parser.css_first(SELECTORS["csrf_token"])
        if not node:
            raise ParseError("CSRF token input not found in HTML")
        return node.attributes.get("value", "")

    def _extract_location_name(self) -> str:
        node = self._parser.css_first(SELECTORS["location"])
        return node.text(strip=True) if node else "Unknown Location"


    def parse_stock_data(self) -> Tuple[str, List[ProductData]]:
        location_name = self._extract_location_name()
        
        products = self._extract_from_scripts()
        if not products:
             log.warning("parser.no_data_found", location=location_name)
             return location_name, []
             
        log.info("parser.scripts_success", location=location_name, items_found=len(products))
        return location_name, products

    def _extract_from_scripts(self) -> List[ProductData]:
        scripts = self._parser.css("script")
        for script in scripts:
            content = script.text()
            if "var purchase_array =" in content:
                match = re.search(r"var\s+purchase_array\s*=\s*(\[.*?\])\s*;", content, re.DOTALL)
                if match:
                    try:
                        raw_data = json.loads(match.group(1))
                        return [
                            {
                                "product": item.get("item_name", "Unknown"),
                                "status": "✅" if item.get("quantity", 0) > 0 else "❌",
                                "quantity": item.get("quantity", 0)
                            }
                            for item in raw_data
                        ]
                    except json.JSONDecodeError as e:
                        log.error("parser.json_error", error=str(e))
        return []