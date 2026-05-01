from playwright.sync_api import sync_playwright
import time

def automate_offer_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.set_default_timeout(60000)

        print("Opening EaseMyTrip Bus page...")
        page.goto("https://www.easemytrip.com/bus/", wait_until="domcontentloaded")
        time.sleep(3)
        print("✅ Bus page loaded!")

        # Click on EMTFIRST offer in Exclusive Offers section
        print("Clicking on EMTFIRST offer in Exclusive Offers...")
        offer = page.locator('a._newrofferbx:has-text("EMTFIRST")').first
        offer.scroll_into_view_if_needed()
        time.sleep(1)
        offer.click()
        time.sleep(3)
        print("✅ EMTFIRST offer clicked!")

        time.sleep(5)
        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    automate_offer_page()
