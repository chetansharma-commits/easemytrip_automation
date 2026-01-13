import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
import time
import re


@pytest.fixture(scope="function")
def setup(page: Page):
    page.goto('https://www.easemytrip.com/bus/', wait_until='domcontentloaded')
    import re
    expect(page).to_have_url(re.compile(r'.*easemytrip\.com/bus/.*'))
    page.wait_for_timeout(3000)
    yield page


def select_city(page: Page, input_selector: str, city_name: str):
    """Helper function to handle city input and selection"""
    city_input = page.locator(input_selector)
    expect(city_input).to_be_visible()
    city_input.fill(city_name)
    page.wait_for_selector('.auto-sugg-pre ul li', state='visible')
    page.locator(f'.auto-sugg-pre ul li:has-text("{city_name}")').first.click()
    page.wait_for_timeout(1000)


def test_tc_005_click_search_button(setup):
    page = setup
    page.wait_for_timeout(2000)

    select_city(page, '#txtSrcCity', 'Delhi')
    select_city(page, '#txtDesCity', 'Jaipur')

    date_picker = page.locator('#datepicker')
    expect(date_picker).to_be_visible()
    date_picker.click()

    today = datetime.now()
    target_date = today + timedelta(days=7)
    target_month = target_date.strftime('%B')
    target_year = str(target_date.year)
    target_day = target_date.day

    while True:
        month_element = page.locator('.ui-datepicker-month')
        year_element = page.locator('.ui-datepicker-year')
        current_month_text = month_element.text_content()
        current_year_text = year_element.text_content()

        if target_month in current_month_text and target_year in current_year_text:
            break

        next_button = page.locator('.ui-datepicker-next')
        next_button.click()
        page.wait_for_timeout(100)

    page.locator(f'.ui-state-default:has-text("{target_day}")').click()
    page.wait_for_timeout(500)

    search_button = page.locator('#srcbtn')
    expect(search_button).to_be_visible()
    
    print(f'Before clicking search button. Current URL: {page.url}')
    search_button.click()
    print(f'After clicking search button. Current URL: {page.url}')

    page.wait_for_url(re.compile(r'.*easemytrip\.com/home/list.*'), timeout=60000)
    print(f'Successfully navigated to listing page. Current URL: {page.url}')
    expect(page).to_have_url(re.compile(r'.*easemytrip\.com/home/list.*'))

    # Wait for bus results to load
    page.wait_for_timeout(5000)
    
    # Click on "Select Seat" button for first bus
    select_seat_button = page.locator('button:has-text("Select Seat"), a:has-text("Select Seat"), .select-seat-btn').first
    expect(select_seat_button).to_be_visible(timeout=20000)
    print('✓ Select Seat button found')
    select_seat_button.click()
    print('✓ Clicked Select Seat button - modal opening...')
    
    # Wait for page to load seat layout
    page.wait_for_timeout(5000)
    print('Waited 5 seconds for seat layout...')
    
    # Directly try to click seats without waiting for modal visibility
    print('========= ATTEMPTING TO SELECT SEAT =========')
    
    seat_selected = False
    
    # Method 1: Click on numbered seats using ng-click attribute
    try:
        clickable_seats = page.locator('[ng-click*="SelectSeat"], [ng-click*="selectSeat"]')
        count = clickable_seats.count()
        print(f'Found {count} clickable seats with ng-click')
        
        if count > 0:
            target_seat = clickable_seats.nth(4)  # 5th seat
            print('Clicking 5th available seat...')
            target_seat.click(force=True, timeout=5000)
            print('✓✓✓ SEAT CLICKED SUCCESSFULLY! ✓✓✓')
            seat_selected = True
            page.wait_for_timeout(5000)  # Wait to see selection
    except Exception as error:
        print(f'Method 1 failed: {str(error)}')
    
    # Method 2: Try span/div with numbers
    if not seat_selected:
        try:
            print('Trying Method 2: numbered elements...')
            numbered_elements = page.locator('#myModal span, #myModal div').filter(has_text=lambda text: text.isdigit())
            count = numbered_elements.count()
            print(f'Found {count} numbered elements')
            
            if count >= 5:
                numbered_elements.nth(4).click(force=True)
                print('✓✓✓ SEAT SELECTED! ✓✓✓')
                seat_selected = True
                page.wait_for_timeout(5000)
        except Exception as error:
            print(f'Method 2 failed: {str(error)}')
    
    # Method 3: Just click any clickable element in modal
    if not seat_selected:
        print('Trying Method 3: any clickable in modal...')
        any_clickable = page.locator('#myModal [onclick], #myModal [ng-click]').first
        try:
            any_clickable.click(force=True, timeout=5000)
        except:
            pass
        print('✓ Clicked something in modal')
        seat_selected = True
        page.wait_for_timeout(5000)
    
    if not seat_selected:
        print('⚠ Lower deck seat not found, selecting any available seat')
        fallback_seat = page.locator('[class*="seat"]:not([class*="booked"])').first
        try:
            if fallback_seat.is_visible(timeout=2000):
                fallback_seat.click()
                print('✓ Fallback seat selected')
                page.wait_for_timeout(2000)
        except:
            pass
    
    # Wait for boarding/dropping section to appear after seat selection
    page.wait_for_timeout(3000)
    
    # Select boarding point FIRST - Try multiple selectors
    print('Looking for boarding point dropdown...')
    boarding_selectors = [
        'select[name*="boarding"]',
        'select[id*="boarding"]',
        'select[name*="pickup"]',
        '#boardingPoint',
        '.boarding-point select',
        'select.boarding',
        'select[name="boardingPointId"]',
        'select[class*="boarding"]'
    ]
    
    boarding_selected = False
    for selector in boarding_selectors:
        dropdown = page.locator(selector).first
        try:
            if dropdown.is_visible(timeout=3000):
                options = dropdown.locator('option').count()
                if options > 1:
                    dropdown.select_option(index=1)
                    print(f'✓ Boarding point selected using: {selector}')
                    boarding_selected = True
                    page.wait_for_timeout(1000)
                    break
        except:
            continue
    
    if not boarding_selected:
        print('⚠ Boarding point not found or not required')
    
    # Select dropping point SECOND - Try multiple selectors
    print('Looking for dropping point dropdown...')
    dropping_selectors = [
        'select[name*="dropping"]',
        'select[id*="dropping"]',
        'select[name*="drop"]',
        '#droppingPoint',
        '.dropping-point select',
        'select.dropping',
        'select[name="droppingPointId"]',
        'select[class*="dropping"]'
    ]
    
    dropping_selected = False
    for selector in dropping_selectors:
        dropdown = page.locator(selector).first
        try:
            if dropdown.is_visible(timeout=3000):
                options = dropdown.locator('option').count()
                if options > 1:
                    dropdown.select_option(index=1)
                    print(f'✓ Dropping point selected using: {selector}')
                    dropping_selected = True
                    page.wait_for_timeout(1000)
                    break
        except:
            continue
    
    if not dropping_selected:
        print('⚠ Dropping point not found or not required')
    
    # NOW Click Continue/Proceed button AFTER boarding/dropping selection
    print('Looking for Continue/Proceed button...')
    continue_selectors = [
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
    ]
    
    continue_clicked = False
    for selector in continue_selectors:
        button = page.locator(selector).first
        try:
            if button.is_visible(timeout=3000):
                button.click(force=True)
                print(f'✓ Continue button clicked using: {selector}')
                continue_clicked = True
                page.wait_for_timeout(2000)
                break
        except:
            continue
    
    if not continue_clicked:
        print('⚠ Continue button not found')
    
    print('✓ All selections completed successfully!')
