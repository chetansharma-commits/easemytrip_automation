import subprocess
import sys
import os
import asyncio

def install_playwright():
    """Installs Playwright and its browsers if not already installed."""
    try:
         ###    __import__('playwright')
        __import__('playwright')
    except ImportError:
        print("Playwright not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            print("\nInstalling browser binaries for Playwright (this might take a moment)...")
            subprocess.check_call([sys.executable, "-m", "playwright", "install"])
            print("Playwright and its browsers installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Playwright or its browsers: {e}")
            sys.exit(1)

async def main():
    """
    This script opens different sections of easemytrip.com using Playwright,
    takes a screenshot, and saves it.
    """
    install_playwright()

    from playwright.async_api import async_playwright, Error

    # Create a directory for screenshots if it doesn't exist
    if not os.path.exists("screenshots_playwright"):
        os.makedirs("screenshots_playwright")

    urls = {
        "flights": "https://www.easemytrip.com/flights.html",
        "hotels": "https://www.easemytrip.com/hotels/",
        "trains": "https://www.easemytrip.com/railways/",
        "bus": "https://www.easemytrip.com/bus/"
    }

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
        except Error as e:
            print(f"Error setting up Playwright browser: {e}")
            print("Please ensure Playwright browsers are installed correctly.")
            return

        for name, url in urls.items():
            try:
                print(f"Loading {name} page: {url}")
                # Go to the page and wait for it to be fully loaded, with a longer timeout
                await page.goto(url, wait_until="load", timeout=60000)
                
                print(f"Page '{name}' is ready.")

                # Take a screenshot
                screenshot_path = os.path.join("screenshots_playwright", f"{name}_page.png")
                await page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")

            except Error as e:
                print(f"An error occurred while loading {name} page: {e}")

        await browser.close()
        print("\nAutomation finished. All pages have been checked.")

if __name__ == "__main__":
    # Check if the script is being run in a compatible environment (e.g., Jupyter)
    try:
        get_ipython()
        # If in an ipython environment, run the async code with a helper
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())
    except NameError:
        # Standard Python environment
        asyncio.run(main())