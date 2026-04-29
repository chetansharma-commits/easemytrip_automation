from playwright.sync_api import sync_playwright

def automate_easemytrip():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("🌐 Navigating to bus.easemytrip.com...")
            page.goto("https://bus.easemytrip.com/")
            print("✅ Website loaded successfully!")
            
            print("🔐 Clicking on sign-in/signup button...")
            page.locator('#divSignInPnl ._btnclick').click()
            print("✅ Sign-in/signup button clicked!")
            page.wait_for_timeout(1000)
            
            print("📝 Clicking on login button...")
            page.locator('#shwlogn').click()
            print("✅ Login button clicked!")
            page.wait_for_timeout(1000)
            
            print("📧 Clicking on email field...")
            page.locator('//*[@id="lgnBox"]/div[1]/div[2]/div/label').click()
            print("✅ Email field clicked!")
            
            print("📧 Entering email...")
            page.locator('//*[@id="lgnBox"]/div[1]/div[2]/div/label').fill("chetan.sharma@easemytrip.com")
            page.keyboard.press("Space")
            page.keyboard.press("Enter")
            print("✅ Email entered and submitted!")
            page.wait_for_timeout(1500)
            
            print("🔘 Clicking continue button...")
            page.locator('//*[@id="shwotp"]').click()
            print("✅ Continue button clicked!")
            page.wait_for_timeout(1000)
            
            print("🔐 Clicking on password field...")
            page.locator('//*[@id="emailgnBox"]/div/div[2]/div/label').click()
            print("✅ Password field clicked!")
            
            print("🔐 Entering password...")
            page.locator('//*[@id="emailgnBox"]/div/div[2]/div/label').fill("Chetan@123")
            print("✅ Password entered!")
            page.wait_for_timeout(500)
            
            print("🔘 Clicking on login button...")
            page.locator('//*[@id="emailgnBox"]/div/div[5]/input').click()
            print("✅ Login button clicked!")
            page.wait_for_timeout(2000)
            
            print("❌ Closing popup...")
            page.evaluate('document.querySelector("._crosslog._crosslogsuccess").click()')
            print("✅ Popup closed!")
            
            print("⏳ Waiting for 5 seconds...")
            page.wait_for_timeout(5000)
            print("✅ Login automation completed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    automate_easemytrip()
