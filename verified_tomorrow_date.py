from playwright.sync_api import sync_playwright
import time

def automate_easemytrip():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Set longer timeout
        page.set_default_timeout(60000)  # 60 seconds
        
        # Navigate to EaseMyTrip bus page
        print("Opening EaseMyTrip Bus page...")
        page.goto("https://www.easemytrip.com/bus/", wait_until="domcontentloaded")
        
        # Wait for page to load
        time.sleep(3)
        print("Page loaded successfully!")
        
        # Select Source City - Delhi
        print("Selecting source city: Delhi...")
        page.fill("#txtSrcCity", "Delhi")
        time.sleep(2)
        page.wait_for_selector('.auto-sugg-pre ul li', state='visible', timeout=10000)
        page.locator('.auto-sugg-pre ul li:has-text("Delhi")').first.click()
        time.sleep(1)
        print("Delhi selected!")
        
        # Select Destination City - Shimla
        print("Selecting destination city: Shimla...")
        page.fill("#txtDesCity", "Shimla")
        time.sleep(2)
        page.wait_for_selector('.auto-sugg-pre ul li', state='visible', timeout=10000)
        page.locator('.auto-sugg-pre ul li:has-text("Shimla")').first.click()
        time.sleep(1)
        print("Shimla selected!")
        
        # Click Tomorrow button
        print("Clicking Tomorrow button...")
        page.locator('.date-controls-sec:has-text("Tomorrow")').first.click(force=True)
        time.sleep(1)
        print("✅ Tomorrow selected!")
        
        # Keep browser open to see results
        time.sleep(10)
        
        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    automate_easemytrip()
