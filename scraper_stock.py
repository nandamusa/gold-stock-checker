from playwright.sync_api import sync_playwright, TimeoutError, Page


def scrape_stock(page: Page) -> tuple[str, list]:
    """
    Returns a tuple: (Location Name, List of Products)
    """
    products = []

    # --- NEW: Extract Location Title ---
    try:
        loc_element = page.locator(".quick-change-location .text")
        if loc_element.is_visible(timeout=5000):
            location_name = loc_element.inner_text().strip()
            print(f"📍 Confirmed Location: {location_name}")
        else:
            location_name = "Unknown Location"
            print("⚠️ Could not find location name element.")
            
    except Exception as e:
        location_name = "Error Reading Location"
        print(f"⚠️ Location scrape error: {e}")

    # --- Product Scraping ---
    try:
        page.wait_for_selector(".ct-body .ctr", timeout=10000)
    except:
        print("❌ Stock table not found.")
        return location_name, []

    rows = page.locator(".ct-body .ctr")
    for i in range(rows.count()):
        row = rows.nth(i)
        
        name = row.locator(".ngc-text").inner_text().split('\n')[0].strip()
        price = row.locator(".item-2").inner_text().replace("Harga", "").strip()
        is_out = row.locator("span.no-stock").is_visible()
        
        products.append({
            "name": name,
            "price": price,
            "status": "❌ OUT" if is_out else "✅ IN",
            "in_stock": not is_out
        })
        
    return location_name, products