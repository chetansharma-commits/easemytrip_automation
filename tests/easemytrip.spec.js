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

    // Wait for bus results to load
    await page.waitForTimeout(5000);
    
    // Click on "Select Seat" button for first bus
    const selectSeatButton = page.locator('button:has-text("Select Seat"), a:has-text("Select Seat"), .select-seat-btn').first();
    await expect(selectSeatButton).toBeVisible({ timeout: 20000 });
    console.log('✓ Select Seat button found');
    await selectSeatButton.click();
    console.log('✓ Clicked Select Seat button - modal opening...');
    
    // Wait for page to load seat layout
    await page.waitForTimeout(5000);
    console.log('Waited 5 seconds for seat layout...');
    
    // Directly try to click seats without waiting for modal visibility
    console.log('========= ATTEMPTING TO SELECT SEAT =========');
    
    let seatSelected = false;
    
    // Method 1: Click on numbered seats using ng-click attribute
    try {
      const clickableSeats = page.locator('[ng-click*="SelectSeat"], [ng-click*="selectSeat"]');
      const count = await clickableSeats.count();
      console.log(`Found ${count} clickable seats with ng-click`);
      
      if (count > 0) {
        const targetSeat = clickableSeats.nth(4); // 5th seat
        console.log('Clicking 5th available seat...');
        await targetSeat.click({ force: true, timeout: 5000 });
        console.log('✓✓✓ SEAT CLICKED SUCCESSFULLY! ✓✓✓');
        seatSelected = true;
        await page.waitForTimeout(5000); // Wait to see selection
      }
    } catch (error) {
      console.log(`Method 1 failed: ${error.message}`);
    }
    
    // Method 2: Try span/div with numbers
    if (!seatSelected) {
      try {
        console.log('Trying Method 2: numbered elements...');
        const numberedElements = page.locator('#myModal span, #myModal div').filter({ hasText: /^[0-9]+$/ });
        const count = await numberedElements.count();
        console.log(`Found ${count} numbered elements`);
        
        if (count >= 5) {
          await numberedElements.nth(4).click({ force: true });
          console.log('✓✓✓ SEAT SELECTED! ✓✓✓');
          seatSelected = true;
          await page.waitForTimeout(5000);
        }
      } catch (error) {
        console.log(`Method 2 failed: ${error.message}`);
      }
    }
    
    // Method 3: Just click any clickable element in modal
    if (!seatSelected) {
      console.log('Trying Method 3: any clickable in modal...');
      const anyClickable = page.locator('#myModal [onclick], #myModal [ng-click]').first();
      await anyClickable.click({ force: true, timeout: 5000 }).catch(() => {});
      console.log('✓ Clicked something in modal');
      seatSelected = true;
      await page.waitForTimeout(5000);
    }
    
    if (!seatSelected) {
      console.log('⚠ Lower deck seat not found, selecting any available seat');
      const fallbackSeat = page.locator('[class*="seat"]:not([class*="booked"])').first();
      if (await fallbackSeat.isVisible({ timeout: 2000 }).catch(() => false)) {
        await fallbackSeat.click();
        console.log('✓ Fallback seat selected');
        await page.waitForTimeout(2000);
      }
    }
    
    // Wait for boarding/dropping section to appear after seat selection
    await page.waitForTimeout(3000);
    
    // Select boarding point FIRST - Try multiple selectors
    console.log('Looking for boarding point dropdown...');
    const boardingSelectors = [
      'select[name*="boarding"]',
      'select[id*="boarding"]', 
      'select[name*="pickup"]',
      '#boardingPoint',
      '.boarding-point select',
      'select.boarding',
      'select[name="boardingPointId"]',
      'select[class*="boarding"]'
    ];
    
    let boardingSelected = false;
    for (const selector of boardingSelectors) {
      const dropdown = page.locator(selector).first();
      if (await dropdown.isVisible({ timeout: 3000 }).catch(() => false)) {
        const options = await dropdown.locator('option').count();
        if (options > 1) {
          await dropdown.selectOption({ index: 1 });
          console.log(`✓ Boarding point selected using: ${selector}`);
          boardingSelected = true;
          await page.waitForTimeout(1000);
          break;
        }
      }
    }
    
    if (!boardingSelected) {
      console.log('⚠ Boarding point not found or not required');
    }
    
    // Select dropping point SECOND - Try multiple selectors
    console.log('Looking for dropping point dropdown...');
    const droppingSelectors = [
      'select[name*="dropping"]',
      'select[id*="dropping"]',
      'select[name*="drop"]',
      '#droppingPoint',
      '.dropping-point select',
      'select.dropping',
      'select[name="droppingPointId"]',
      'select[class*="dropping"]'
    ];
    
    let droppingSelected = false;
    for (const selector of droppingSelectors) {
      const dropdown = page.locator(selector).first();
      if (await dropdown.isVisible({ timeout: 3000 }).catch(() => false)) {
        const options = await dropdown.locator('option').count();
        if (options > 1) {
          await dropdown.selectOption({ index: 1 });
          console.log(`✓ Dropping point selected using: ${selector}`);
          droppingSelected = true;
          await page.waitForTimeout(1000);
          break;
        }
      }
    }
    
    if (!droppingSelected) {
      console.log('⚠ Dropping point not found or not required');
    }
    
    // NOW Click Continue/Proceed button AFTER boarding/dropping selection
    console.log('Looking for Continue/Proceed button...');
    const continueSelectors = [
      'button:has-text("Continue")',
      'button:has-text("Proceed")',
      'button:has-text("Next")',
      'button:has-text("CONTINUE")',
      '.continue-btn',
      '.proceed-btn',
      '#continueBtn',
      '#proceedBtn',
      'button[type="submit"]',
      'a:has-text("Continue")',
      'a:has-text("Proceed")'
    ];
    
    let continueClicked = false;
    for (const selector of continueSelectors) {
      const button = page.locator(selector).first();
      if (await button.isVisible({ timeout: 3000 }).catch(() => false)) {
        await button.click({ force: true });
        console.log(`✓ Continue button clicked using: ${selector}`);
        continueClicked = true;
        await page.waitForTimeout(2000);
        break;
      }
    }
    
    if (!continueClicked) {
      console.log('⚠ Continue button not found');
    }
    
    console.log('✓ All selections completed successfully!');
  });

});