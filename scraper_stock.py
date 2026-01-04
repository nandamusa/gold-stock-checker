from playwright.sync_api import sync_playwright, TimeoutError, Page


def scrape_stock(page: Page) -> list:
    products = []

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
        
    return products