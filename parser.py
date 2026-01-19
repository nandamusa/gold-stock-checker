from typing import List, Optional, Tuple, TypedDict
from selectolax.lexbor import LexborHTMLParser, LexborNode

from config import SELECTORS
from exceptions import ParseError
from logger import log


class ProductData(TypedDict):
    product: str
    status: str

class Parser:
    """
    Parses HTML content. 
    Designed to be instantiated once per HTML response.
    """
    
    def __init__(self, html: str):
        if not html:
            raise ParseError("Cannot parse empty HTML")
        self._parser = LexborHTMLParser(html)

    def get_csrf_token(self) -> str:
        """Extracts CSRF token for login flows."""
        node = self._parser.css_first(SELECTORS["csrf_token"])
        if not node:
            raise ParseError("CSRF token input not found in HTML")
        return node.attributes.get("value", "")

    def _extract_location_name(self) -> str:
        node = self._parser.css_first(SELECTORS["location"])
        return node.text(strip=True) if node else "Unknown Location"

    def _parse_row(self, row: LexborNode) -> Optional[ProductData]:
        """Parses a single product row."""
        item_node = row.css_first(SELECTORS["row_item"])
        if not item_node:
            return None

        name_node = item_node.css_first(SELECTORS["item_name"])
        if not name_node:
            return None
        
        raw_text = name_node.text(strip=True, separator="|")
        clean_name = raw_text.split("|")[0].strip() if raw_text else "Unknown Product"

        is_out_of_stock = item_node.css_first(SELECTORS["out_of_stock"]) is not None
        status_icon = "❌" if is_out_of_stock else "✅"

        return {"product": clean_name, "status": status_icon}

    def parse_stock_data(self) -> Tuple[str, List[ProductData]]:
        """
        Main entry point to extract stock data.
        Returns: (Location Name, List of Products)
        """
        location_name = self._extract_location_name()
        rows = self._parser.css(SELECTORS["rows"])
        
        if not rows:
            log.warning("parser.no_rows_found", location=location_name)
            return location_name, []

        products: List[ProductData] = []
        for row in rows:
            if data := self._parse_row(row):
                products.append(data)

        return location_name, products