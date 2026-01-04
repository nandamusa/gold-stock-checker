from playwright.sync_api import sync_playwright, TimeoutError, Page


def scrape_stock(page: Page) -> tuple[str, list]:
    """
    Returns a tuple: (Location Name, List of Products)
    """
    products = []

    # --- NEW: Extract Location Title ---
    location_name = "Unknown Location" # Default fallback
    try:
        loc_element = page.locator(".quick-change-location .text")
        loc_element.wait_for(state="visible", timeout=5000)

        location_name = loc_element.inner_text().strip()
        print(f"📍 Confirmed Location: {location_name}")
            
    except Exception as e:
        print(f"⚠️ Could not read location (Page might be loading): {e}")

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