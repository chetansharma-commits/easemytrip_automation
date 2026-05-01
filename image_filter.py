from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime, timedelta

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
        
        # Select Date (5 days from today)
        print("Selecting date (5 days from today)...")
        page.click("#datepicker")
        time.sleep(2)
        
        # Calculate 5 days from today
        target_date = datetime.now() + timedelta(days=5)
        target_day = str(target_date.day)
        target_month = target_date.month
        target_year = target_date.year
        
        # Navigate calendar to the correct month/year
        for _ in range(12):  # max 12 forward navigations
            # Read current month and year from calendar header
            try:
                month_text = page.locator('.ui-datepicker-month').inner_text(timeout=3000)
                year_text = page.locator('.ui-datepicker-year').inner_text(timeout=3000)
            except:
                month_text = page.locator('.ui-datepicker-title').inner_text(timeout=3000)
                year_text = ""
            
            month_map = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            
            cal_month = None
            for name, num in month_map.items():
                if name.lower() in month_text.lower():
                    cal_month = num
                    break
            
            cal_year = int(year_text.strip()) if year_text.strip().isdigit() else target_year
            
            print(f"   Calendar showing: {month_text} {cal_year}, Target: month={target_month} year={target_year}")
            
            if cal_month == target_month and cal_year == target_year:
                break
            
            # Click next month button
            page.locator('.ui-datepicker-next').click()
            time.sleep(1)
        
        # Now click the correct day
        page.locator(f'td[data-handler="selectDay"] a.ui-state-default:text-is("{target_day}")').first.click(force=True)
        time.sleep(1)
        print(f"✅ Date selected: {target_date.strftime('%d %B %Y')}")
        
        # Click Search button
        print("Clicking search button...")
        page.click("#srcbtn")
        print("✅ Search clicked!")
        try:
            page.wait_for_url(re.compile(r'.*easemytrip\.com/home/list.*'), timeout=30000)
        except:
            pass
        time.sleep(5)
        print("✅ Bus list loaded!")

        # Click Top Rated filter
        print("Clicking Top Rated filter...")
        page.locator('[ng-click*="toprated"]').first.click(force=True)
        time.sleep(3)
        print("✅ Top Rated filter applied!")

        # Click Luxury filter
        print("Clicking Luxury filter...")
        page.locator('[ng-click*="luxury"]').first.click(force=True)
        time.sleep(3)
        print("✅ Luxury filter applied!")

        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    automate_easemytrip()
