import os
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError

from telegram import send_telegram
from scraper_stock import scrape_stock

load_dotenv()

TARGET_URL = os.getenv("TARGET_URL")
USER_AGENT = os.getenv("USER_AGENT")


def run_stock_checker():
    with sync_playwright() as p:
        print("🚀 Launching Browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir="./user_data",
            # headless=False,
            channel="chrome",
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 720},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            geolocation={"latitude": -6.1936, "longitude": 106.8912}, #pulogadung
            permissions=["geolocation"],
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars"]
        )

        page = context.pages[0]
        
        # Hide automation footprint
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            print(f"🌍 Navigating to {TARGET_URL}")
            page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
        except TimeoutError:
            print("⚠️ Initial load timed out. Proceeding...")

        # 1. Handle Initial Confirmation Popup
        popup_confirmation = page.locator(".swal-button--confirm")
        try:
            popup_confirmation.wait_for(state="visible", timeout=10000)
            popup_confirmation.click()
            print("✅ Initial confirmation clicked.")
        except TimeoutError:
            print("⏩ No initial confirmation popup found.")

        # 2. Scrape Data
        location_name, products = scrape_stock(page)

        if products:
            all_items_list = [
                f"🔹 *{p['name']}*\nStatus: {p['status']} -> Price: {p['price']}" 
                for p in products
            ]
            
            now = datetime.now().strftime("%H:%M:%S")
            header = f"📊 *ANTAM FULL STOCK REPORT*\n📍 {location_name}\n🕒 Time: {now}\n"
            alert_msg = header + "\n" + "—" * 15 + "\n\n" + "\n\n".join(all_items_list)
            
            # 3. Send
            send_telegram(alert_msg)
            print(f"✅ Full report ({len(products)} items) sent to Telegram.")
        else:
            print("❌ Failed: Product list is empty.")

        print("✅ Session finished. Close the browser.")
        context.close()

if __name__ == "__main__":
    run_stock_checker()