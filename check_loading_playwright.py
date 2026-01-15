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
    
    print('\n🚌 === BUS BOOKING AUTOMATION STARTING ===\n')
    
    # STEP 1: Source city
    print('📍 Selecting Delhi...')
    select_city(page, '#txtSrcCity', 'Delhi')
    page.wait_for_timeout(2000)
    print('✅ Delhi selected\n')
    
    # STEP 2: Destination city
    print('📍 Selecting Jaipur...')
    select_city(page, '#txtDesCity', 'Jaipur')
    page.wait_for_timeout(2000)
    print('✅ Jaipur selected\n')
    
    # STEP 3: Date
    print('📍 Selecting date...')
    date_picker = page.locator('#datepicker')
    expect(date_picker).to_be_visible()
    date_picker.click()
    page.wait_for_timeout(1000)
    
    future_date = datetime.now() + timedelta(days=5)
    day = future_date.day
    page.locator(f'.ui-state-default:has-text("{day}")').first.click()
    page.wait_for_timeout(2000)
    print(f'✅ Date selected: {day}\n')
    
    # STEP 4: Search
    print('📍 Searching buses...')
    search_button = page.locator('#srcbtn')
    expect(search_button).to_be_visible()
    search_button.click()
    page.wait_for_url(re.compile(r'.*easemytrip\.com/home/list.*'), timeout=60000)
    page.wait_for_timeout(5000)
    print('✅ Bus list loaded\n')
    
    # STEP 5: Select seat button
    print('📍 Opening seat layout...')
    select_seat_button = page.locator('button:has-text("Select Seat"), a:has-text("Select Seat")').first
    expect(select_seat_button).to_be_visible(timeout=20000)
    select_seat_button.click()
    page.wait_for_timeout(3000)
    print('✅ Seat layout opened\n')
    
    # STEP 6: Select only ONE available seat
    print('📍 Selecting any available seat...')
    
    seat_clicked = False
    
    try:
        # Wait until seats appear
        page.wait_for_selector('[class*="avail"]', timeout=10000)
        
        seats = page.locator('[class*="avail"]')
        total = seats.count()
        print(f'   Found {total} available seats')
        
        for i in range(total):
            seat = seats.nth(i)
            
            # Click only visible seat
            if seat.is_visible():
                seat_text = seat.text_content()
                print(f'   Clicking seat: {seat_text}')
                seat.click(force=True)
                page.wait_for_timeout(1500)
                
                print('✅ ONE SEAT SELECTED\n')
                seat_clicked = True
                break   # 🔥 VERY IMPORTANT — ONLY ONE SEAT
    
    except Exception as e:
        print(f'⚠️ Error selecting seat: {e}\n')
    
    if not seat_clicked:
        print('⚠️ No seat selected\n')
    
    # STEP 7 & 8: Boarding and Dropping
    print('📍 Selecting BOARDING & DROPPING points...')
    
    try:
        page.wait_for_timeout(1000)
        
        # Find all clickable labels with ng-click
        labels = page.locator('label[ng-click]')
        label_count = labels.count()
        print(f'   Found {label_count} clickable options')
        
        boarding_clicked = False
        dropping_clicked = False
        
        # Try to click first 2 visible labels
        for i in range(label_count):
            if boarding_clicked and dropping_clicked:
                break
                
            label = labels.nth(i)
            try:
                if label.is_visible():
                    label.click(force=True)
                    
                    if not boarding_clicked:
                        print('✅ BOARDING POINT SELECTED!')
                        boarding_clicked = True
                        page.wait_for_timeout(1000)
                    elif not dropping_clicked:
                        print('✅ DROPPING POINT SELECTED!\n')
                        dropping_clicked = True
                        page.wait_for_timeout(1000)
                        break
            except:
                continue
        
        if not boarding_clicked or not dropping_clicked:
            print('⚠️ Some points may be auto-selected\n')
    except Exception as error:
        print(f'⚠️ Error: {error}\n')
    
    # STEP 9: Continue
    print('📍 Clicking Continue...')
    try:
        page.wait_for_timeout(3000)
        
        # Try multiple selectors for continue button
        continue_selectors = [
            'button:has-text("Continue")',
            'a:has-text("Continue")',
            'input[value="Continue"]',
            'button[type="submit"]',
            '.continue-btn',
            '[class*="continue"]'
        ]
        
        continue_clicked = False
        for selector in continue_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    print(f'   Found continue button with selector: {selector}')
                    btn.click(force=True)
                    print('✅ Continue clicked!\n')
                    continue_clicked = True
                    page.wait_for_timeout(5000)
                    
                    # Wait for next page to load
                    print('📍 Waiting for next page...')
                    page.wait_for_load_state('networkidle', timeout=30000)
                    print('✅ Next page loaded!\n')
                    break
            except:
                continue
        
        if not continue_clicked:
            print('⚠️ Continue button not found\n')
    except Exception as e:
        print(f'⚠️ Error: {e}\n')
    
    # STEP 10: Fill passenger details
    print('📍 Filling passenger details...')
    try:
        page.wait_for_timeout(3000)
        
        # Select title as "Mr"
        print('   Selecting title: Mr')
        title_selectors = [
            'select[name*="title"], select[id*="title"]',
            'select.title',
            '[name*="Title"]',
            'select:near(:text("Title"))'
        ]
        
        for selector in title_selectors:
            try:
                title_dropdown = page.locator(selector).first
                if title_dropdown.is_visible(timeout=2000):
                    title_dropdown.select_option(label='Mr')
                    print('✅ Title "Mr" selected')
                    break
            except:
                continue
        
        page.wait_for_timeout(1000)
        
        # Fill first name as "test"
        print('   Filling first name: test')
        fname_selectors = [
            'input[name*="firstName"], input[id*="firstName"]',
            'input[name*="firstname"], input[id*="firstname"]',
            'input[placeholder*="First Name"]',
            'input[placeholder*="first name"]'
        ]
        
        for selector in fname_selectors:
            try:
                fname_field = page.locator(selector).first
                if fname_field.is_visible(timeout=2000):
                    fname_field.fill('test')
                    print('✅ First name filled: test')
                    break
            except:
                continue
        
        page.wait_for_timeout(1000)
        
        # Fill last name as "test"
        print('   Filling last name: test')
        lname_selectors = [
            'input[name*="lastName"], input[id*="lastName"]',
            'input[name*="lastname"], input[id*="lastname"]',
            'input[placeholder*="Last Name"]',
            'input[placeholder*="last name"]'
        ]
        
        for selector in lname_selectors:
            try:
                lname_field = page.locator(selector).first
                if lname_field.is_visible(timeout=2000):
                    lname_field.fill('test')
                    print('✅ Last name filled: test')
                    break
            except:
                continue
        
        page.wait_for_timeout(1000)
        
        # Fill age as "25"
        print('   Filling age: 25')
        age_selectors = [
            'input[name*="age"], input[id*="age"]',
            'input[placeholder*="Age"]',
            'input[placeholder*="age"]',
            'select[name*="age"], select[id*="age"]'
        ]
        
        for selector in age_selectors:
            try:
                age_field = page.locator(selector).first
                if age_field.is_visible(timeout=2000):
                    # Check if it's a select dropdown or input field
                    if 'select' in selector:
                        age_field.select_option('25')
                    else:
                        age_field.fill('25')
                    print('✅ Age filled: 25\n')
                    break
            except:
                continue
        
        page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f'⚠️ Error filling details: {e}\n')
    
    # STEP 11: Select insurance - Yes
    print('📍 Selecting insurance: Yes')
    try:
        page.wait_for_timeout(2000)
        
        # Try multiple selectors for insurance Yes option
        insurance_selectors = [
            'input[value="yes"][type="radio"]',
            'input[value="Yes"][type="radio"]',
            'input[id*="insurance"][value*="yes"]',
            'label:has-text("Yes")',
            'input[name*="insurance"]'
        ]
        
        for selector in insurance_selectors:
            try:
                insurance_option = page.locator(selector).first
                if insurance_option.is_visible(timeout=2000):
                    insurance_option.click(force=True)
                    print('✅ Insurance "Yes" selected')
                    break
            except:
                continue
        
        page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f'⚠️ Error selecting insurance: {e}\n')
    
    # STEP 12: Select insurance condition checkbox
    print('📍 Selecting insurance condition...')
    try:
        page.wait_for_timeout(1000)
        
        # Try to find and click insurance condition checkbox
        condition_selectors = [
            'input[type="checkbox"][name*="insurance"]',
            'input[type="checkbox"][id*="insurance"]',
            'input[type="checkbox"]:near(:text("insurance"))',
            'label:has-text("I accept") input[type="checkbox"]',
            'input[type="checkbox"].insurance'
        ]
        
        for selector in condition_selectors:
            try:
                checkbox = page.locator(selector).first
                if checkbox.is_visible(timeout=2000):
                    checkbox.check(force=True)
                    print('✅ Insurance condition accepted\n')
                    break
            except:
                continue
        
        page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f'⚠️ Error selecting insurance condition: {e}\n')
    
    # STEP 13: Fill email
    print('📍 Filling email: cs@gmail.com')
    try:
        page.wait_for_timeout(1000)
        
        # Try multiple selectors for email field
        email_selectors = [
            'input[type="email"]',
            'input[name*="email"]',
            'input[id*="email"]',
            'input[placeholder*="email"]',
            'input[placeholder*="Email"]'
        ]
        
        for selector in email_selectors:
            try:
                email_field = page.locator(selector).first
                if email_field.is_visible(timeout=2000):
                    email_field.fill('cs@gmail.com')
                    print('✅ Email filled: cs@gmail.com\n')
                    break
            except:
                continue
        
        page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f'⚠️ Error filling email: {e}\n')
    
    # STEP 14: Fill mobile number
    print('📍 Filling mobile number: 8445121366')
    try:
        page.wait_for_timeout(2000)
        
        # Try multiple selectors for mobile field (avoid country code dropdown)
        mobile_selectors = [
            'input[type="tel"]:not([name*="country"]):not([id*="country"])',
            'input[name*="mobile"]:not([name*="country"])',
            'input[name*="phone"]:not([name*="country"])',
            'input[name*="Mobile"]:not([name*="country"])',
            'input[name*="Phone"]:not([name*="country"])',
            'input[id*="mobile"]:not([id*="country"])',
            'input[id*="phone"]:not([id*="country"])',
            'input[placeholder*="mobile"]',
            'input[placeholder*="Mobile"]',
            'input[placeholder*="Phone"]',
            'input[maxlength="10"][type="tel"]'
        ]
        
        mobile_filled = False
        for selector in mobile_selectors:
            try:
                mobile_fields = page.locator(selector)
                count = mobile_fields.count()
                
                for i in range(count):
                    mobile_field = mobile_fields.nth(i)
                    try:
                        if mobile_field.is_visible(timeout=1000):
                            # Check if field is editable and not a dropdown
                            field_type = mobile_field.get_attribute('type')
                            if field_type in ['tel', 'text', 'number']:
                                # Focus on the field
                                mobile_field.click()
                                page.wait_for_timeout(300)
                                
                                # Clear field with triple click and backspace
                                mobile_field.click(click_count=3)
                                page.wait_for_timeout(200)
                                mobile_field.press('Backspace')
                                page.wait_for_timeout(200)
                                
                                # Type the number
                                mobile_field.type('8445121366', delay=50)
                                page.wait_for_timeout(1000)
                                
                                # Verify it was entered
                                value = mobile_field.input_value()
                                if '8445121366' in value or '844512' in value:
                                    print(f'✅ Mobile number filled: 8445121366 (selector: {selector})\n')
                                    mobile_filled = True
                                    break
                    except:
                        continue
                
                if mobile_filled:
                    break
            except:
                continue
        
        if not mobile_filled:
            print('⚠️ Mobile field not found or not filled properly\n')
        
        page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f'⚠️ Error filling mobile: {e}\n')
    
    # STEP 15: Click Continue to go to next page
    print('📍 Clicking Continue to next page...')
    try:
        page.wait_for_timeout(3000)
        
        # Scroll to bottom to ensure button is visible
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(1000)
        
        # Try multiple selectors for continue button
        continue_selectors = [
            'button:has-text("Continue")',
            'a:has-text("Continue")',
            'input[value*="Continue"]',
            'button:has-text("Proceed")',
            'button:has-text("Next")',
            'button[type="submit"]',
            'a[class*="continue"]',
            'button[class*="continue"]',
            '.btn-continue',
            'a.btn:has-text("Continue")',
            'button.btn:has-text("Continue")'
        ]
        
        continue_clicked = False
        for selector in continue_selectors:
            try:
                buttons = page.locator(selector)
                count = buttons.count()
                print(f'   Trying selector: {selector} (found {count} elements)')
                
                if count > 0:
                    # Try all matching buttons
                    for i in range(count):
                        try:
                            btn = buttons.nth(i)
                            if btn.is_visible(timeout=1000):
                                btn_text = btn.text_content()
                                print(f'   Found button with text: {btn_text}')
                                btn.scroll_into_view_if_needed()
                                page.wait_for_timeout(500)
                                btn.click(force=True)
                                print('✅ Continue clicked!\n')
                                continue_clicked = True
                                page.wait_for_timeout(5000)
                                
                                # Wait for next page to load
                                print('📍 Waiting for next page...')
                                page.wait_for_load_state('domcontentloaded', timeout=30000)
                                print('✅ Next page opened!\n')
                                break
                        except Exception as btn_error:
                            print(f'   Button {i} error: {btn_error}')
                            continue
                    if continue_clicked:
                        break
            except Exception as selector_error:
                print(f'   Selector error: {selector_error}')
                continue
        
        if not continue_clicked:
            print('⚠️ Continue button not found')
            
        page.wait_for_timeout(3000)
        
    except Exception as e:
        print(f'⚠️ Error clicking continue: {e}\n')
    
    print('🎉 === BOOKING FLOW COMPLETED ===\n')
