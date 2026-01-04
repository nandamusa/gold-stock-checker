import os
import time
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError, Page

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
            popup_confirmation.wait_for(state="visible", timeout=5000)
            popup_confirmation.click()
            print("✅ Initial confirmation clicked.")
        except TimeoutError:
            print("⏩ No initial confirmation popup found.")

        # # 2. Change Location
        # print("📍 Changing location to Pulo Gadung...")
        # try:
        #     page.locator("#btnChangeLocation").click()
        #     page.locator("#select2-location-container").wait_for(state="visible")
        #     page.locator("#select2-location-container").click()
            
        #     target_option = page.locator(".select2-results__option").filter(
        #         has_text="BELM - Pengiriman Ekspedisi, Pulogadung Jakarta, Jakarta"
        #     )
        #     target_option.first.click()
            
        #     page.locator("#change-location-button").click()
        #     print("🔄 Location set. Waiting for reload...")
        #     page.wait_for_load_state("networkidle")
        #     time.sleep(3) # Extra buffer for price JS
        # except Exception as e:
        #     print(f"❌ Failed to change location: {e}")

        # 3. Scrape Data
        products = scrape_stock(page)

        if products:
            all_items_list = [
                f"🔹 *{p['name']}*\nStatus: {p['status']}\nPrice: {p['price']}" 
                for p in products
            ]
            
            now = datetime.now().strftime("%H:%M:%S")
            
            # 3. Construct final message
            header = f"📊 *ANTAM FULL STOCK REPORT*\n🕒 Time: {now}\n"
            alert_msg = header + "\n" + "—" * 15 + "\n\n" + "\n\n".join(all_items_list)
            
            # 4. Send
            send_telegram(alert_msg)
            print(f"✅ Full report ({len(products)} items) sent to Telegram.")
        else:
            print("❌ Failed: Product list is empty.")

        print("✅ Session finished. Close the browser.")
        context.close()

if __name__ == "__main__":
    run_stock_checker()