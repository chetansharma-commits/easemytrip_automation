const { test, expect } = require('@playwright/test');

test.describe('EaseMyTrip Bus Booking Automation', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.easemytrip.com/bus/', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/.*easemytrip.com\/bus\//);
    await page.waitForTimeout(3000);
  });

  // Helper function to handle city input and selection
  async function selectCity(page, inputSelector, cityName) { 
    const cityInput = page.locator(inputSelector);
    await expect(cityInput).toBeVisible();
    await cityInput.fill(cityName);
    await page.waitForSelector('.auto-sugg-pre ul li', { state: 'visible' }); 
    await page.locator(`.auto-sugg-pre ul li:has-text("${cityName}")`).first().click();
    await page.waitForTimeout(1000);
  }

  test('TC_005_Click Search Button', async ({ page }) => {
    await page.waitForTimeout(2000); 

    await selectCity(page, '#txtSrcCity', 'Delhi');
    await selectCity(page, '#txtDesCity', 'Jaipur');

    const datePicker = page.locator('#datepicker');
    await expect(datePicker).toBeVisible();
    await datePicker.click(); 

    const today = new Date();
    today.setDate(today.getDate() + 7);
    const targetMonth = today.toLocaleString('default', { month: 'long' });
    const targetYear = today.getFullYear();
    const targetDay = today.getDate();

    let currentMonthText = '';
    let currentYearText = '';
    while (true) {
        const monthElement = page.locator('.ui-datepicker-month');
        const yearElement = page.locator('.ui-datepicker-year');
        currentMonthText = await monthElement.textContent();
        currentYearText = await yearElement.textContent();

        if (currentMonthText.includes(targetMonth) && currentYearText.includes(String(targetYear))) {
            break;
        }

        const nextButton = page.locator('.ui-datepicker-next');
        await nextButton.click();
        await page.waitForTimeout(100);
    }
    await page.locator(`.ui-state-default:has-text("${targetDay}")`).click();
    await page.waitForTimeout(500);

    const searchButton = page.locator('#srcbtn'); 
    await expect(searchButton).toBeVisible();
    
    console.log('Before clicking search button. Current URL:', page.url()); 
    await searchButton.click();
    console.log('After clicking search button. Current URL:', page.url()); 

    await page.waitForURL(/.*easemytrip.com\/home\/list/, { timeout: 60000 });
    console.log('Successfully navigated to listing page. Current URL:', page.url()); 
    await expect(page).toHaveURL(/.*easemytrip.com\/home\/list/);
  });

});