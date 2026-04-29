from playwright.sync_api import sync_playwright
import time
from datetime import datetime, timedelta
import re

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
        
        # Click Search button and wait for results page
        print("Clicking search button...")
        page.click("#srcbtn")
        print("Waiting for bus list to load...")
        
        # Wait for URL to change to results page
        try:
            page.wait_for_url(re.compile(r'.*easemytrip\.com/home/list.*'), timeout=60000)
        except:
            print("URL didn't change, but continuing...")
        
        time.sleep(5)
        print("✅ Bus list loaded!")
        
        # ===== APPLY GPS ENABLED FILTER =====
        print("\n🔍 === APPLYING GPS ENABLED FILTER ===\n")
        time.sleep(2)
        
        gps_elem = None
        
        print("📍 Applying GPS Enabled filter...")
        try:
            gps_selectors = [
                'input[type="checkbox"][value*="GPS"]',
                'input[type="checkbox"][id*="gps"]',
                'label:has-text("GPS Enabled")',
                'label:has-text("GPS")'
            ]
            
            filter_applied = False
            for selector in gps_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=3000):
                        elem.click(force=True)
                        print("   ✅ GPS Enabled filter applied!")
                        gps_elem = elem
                        filter_applied = True
                        time.sleep(3)
                        break
                except:
                    continue
            
            if not filter_applied:
                print("   ⚠️ GPS Enabled filter not found")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        
        print("")
        time.sleep(5)
        
        # ===== CLICK ON AMENITIES LISTING =====
        print("\n🎯 === CLICKING AMENITIES LISTING ===\n")
        time.sleep(2)
        
        print("📍 Looking for Amenities option...")
        try:
            amenities_selectors = [
                'li:has-text("Amenities")',
                'a:has-text("Amenities")',
                'div:has-text("Amenities")',
                'span:has-text("Amenities")',
                'label:has-text("Amenities")',
                '[class*="ameniti"]'
            ]
            
            amenities_clicked = False
            for selector in amenities_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=3000):
                        elem.click(force=True)
                        print("   ✅ Amenities listing clicked!")
                        amenities_clicked = True
                        time.sleep(3)
                        break
                except:
                    continue
            
            if not amenities_clicked:
                print("   ⚠️ Amenities option not found")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        
        print("")
        time.sleep(3)
        
        print("\n✅ Done!\n")
        time.sleep(5)
        
        # Keep browser open to see final results
        print("Keeping browser open for 10 seconds...")
        time.sleep(10)
        
        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    automate_easemytrip()
