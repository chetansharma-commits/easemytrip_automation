from playwright.sync_api import sync_playwright
import time

def automate_popular_bus_route():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.set_default_timeout(60000)

        print("Opening EaseMyTrip Bus page...")
        page.goto("https://www.easemytrip.com/bus/", wait_until="domcontentloaded")
        time.sleep(3)
        print("✅ Bus page loaded!")

        # Click on Bengaluru to Hyderabad in Popular Bus Routes
        print("Clicking on Bengaluru to Hyderabad...")
        route = page.locator('a[href*="bengaluru-to-hyderabad-bus-tickets"]').first
        route.scroll_into_view_if_needed()
        time.sleep(1)
        route.click()
        time.sleep(3)
        print("✅ Bengaluru to Hyderabad clicked!")

        time.sleep(5)
        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    automate_popular_bus_route()
