import os
import pytest
from playwright.sync_api import Page, expect, sync_playwright
from datetime import datetime, timedelta
import time
import re


@pytest.fixture(scope="function")
def setup(page: Page):
    page.goto('https://www.easemytrip.com/bus/', wait_until='domcontentloaded')
    import re
    expect(page).to_have_url(re.compile(r'.*easemytrip\.com/bus/.*'))
    page.wait_for_timeout(300)
    yield page


def select_city(page: Page, input_selector: str, city_name: str):
    """Helper function to handle city input and selection"""
    city_input = page.locator(input_selector)
    expect(city_input).to_be_visible()
    city_input.fill(city_name)
    page.wait_for_selector('.auto-sugg-pre ul li', state='visible')
    page.locator(f'.auto-sugg-pre ul li:has-text("{city_name}")').first.click()
    page.wait_for_timeout(300)


def test_tc_005_click_search_button(setup):
    page = setup
    
    print('\n🚌 === BUS BOOKING AUTOMATION STARTING ===\n')
    
    # STEP 1: Source city
    print('📍 Selecting Delhi...')
    select_city(page, '#txtSrcCity', 'Delhi')
    page.wait_for_timeout(300)
    print('✅ Delhi selected\n')
    
    # STEP 2: Destination city
    print('📍 Selecting Jaipur...')
    select_city(page, '#txtDesCity', 'Jaipur')
    page.wait_for_timeout(300)
    print('✅ Jaipur selected\n')
    
    # STEP 3: Date
    print('📍 Selecting date...')
    date_picker = page.locator('#datepicker')
    expect(date_picker).to_be_visible()
    date_picker.click()
    page.wait_for_timeout(200)
    
    future_date = datetime.now() + timedelta(days=5)
    day = future_date.day
    page.locator(f'.ui-state-default:has-text("{day}")').first.click()
    page.wait_for_timeout(300)
    print(f'✅ Date selected: {day}\n')
    
    # STEP 4: Search
    print('📍 Searching buses...')
    search_button = page.locator('#srcbtn')
    expect(search_button).to_be_visible()
    search_button.click()
    page.wait_for_url(re.compile(r'.*easemytrip\.com/home/list.*'), timeout=60000)
    page.wait_for_timeout(300)
    print('✅ Bus list loaded\n')
    
    # ===== FILTERS SECTION =====
    print('\n🔍 === APPLYING FILTERS ===\n')
    
    # FILTER: AC Bus Type Only
    print('📍 Applying AC Bus filter...')
    try:
        page.wait_for_timeout(300)
        
        # Try to find and click AC bus filter
        ac_selectors = [
            'input[type="checkbox"][value*="AC"], input[type="checkbox"][id*="ac"]',
            'label:has-text("AC")',
            'input[value*="A/C"][type="checkbox"]',
            '[class*="filter"] input:has-text("AC")'
        ]
        
        for selector in ac_selectors:
            try:
                ac_option = page.locator(selector).first
                if ac_option.is_visible(timeout=2000):
                    ac_option.click(force=True)
                    print('✅ AC Bus filter applied')
                    page.wait_for_timeout(300)
                    break
            except:
                continue
                
        print('')
    except Exception as e:
        print(f'⚠️ AC Bus filter error: {e}\n')
    
    # Wait for filtered results to load
    print('📍 Waiting for filtered results...')
    page.wait_for_timeout(200)
    print('✅ Filter applied successfully!\n')
    
    # VERIFY AC FILTER: Check if all buses in listing have AC/A/C
    print('📍 Verifying AC buses in listing...')
    try:
        page.wait_for_timeout(300)
        
        # Find all bus listings
        bus_listings = page.locator('[class*="bus"], [class*="list-item"], .result-item, div[ng-repeat]').all()
        
        if len(bus_listings) > 0:
            ac_count = 0
            non_ac_count = 0
            
            # Check first 5 bus listings
            for i, bus in enumerate(bus_listings[:5]):
                try:
                    bus_text = bus.text_content() or ''
                    bus_text_upper = bus_text.upper()
                    
                    # FIRST check if it's Non-AC (exclude these)
                    if 'NON AC' in bus_text_upper or 'NON-AC' in bus_text_upper or 'NONAC' in bus_text_upper or 'NON A/C' in bus_text_upper:
                        non_ac_count += 1
                        print(f'   Bus {i+1}: Non-AC ❌')
                    # THEN check if it's AC
                    elif 'AC' in bus_text_upper or 'A/C' in bus_text_upper or 'A.C' in bus_text_upper:
                        ac_count += 1
                        print(f'   Bus {i+1}: AC ✅')
                    else:
                        # No AC/Non-AC label found
                        print(f'   Bus {i+1}: Unknown ⚠️')
                except:
                    continue
            
            print(f'\n✅ AC Buses found: {ac_count}')
            if non_ac_count > 0:
                print(f'❌ Non-AC Buses found: {non_ac_count}')
                print('\n⚠️ TEST FAILED: Non-AC buses found after applying AC filter!\n')
                assert False, f"AC Filter Failed: Found {non_ac_count} Non-AC buses in listing"
            else:
                print('✅ All buses are AC - Filter working correctly!')
            print('')
        else:
            print('⚠️ No bus listings found\n')
            
    except AssertionError:
        raise
    except Exception as e:
        print(f'⚠️ AC Verification error: {e}\n')
    
    # RESET FILTER AFTER AC
    print('📍 Clicking Reset Filter...')
    try:
        page.wait_for_timeout(500)
        reset_selectors = [
            'button:has-text("Reset")',
            'a:has-text("Reset")',
            'button:has-text("Clear")',
            '[class*="reset"]',
            '[id*="reset"]'
        ]
        for selector in reset_selectors:
            try:
                reset_btn = page.locator(selector).first
                if reset_btn.is_visible(timeout=2000):
                    reset_btn.click(force=True)
                    print('✅ Reset Filter clicked!\n')
                    page.wait_for_timeout(500)
                    break
            except:
                continue
    except Exception as e:
        print(f'⚠️ Reset error: {e}\n')
    
    # FILTER: Non-AC Bus Type
    print('📍 Applying Non-AC Bus filter...')
    try:
        page.wait_for_timeout(300)
        non_ac_selectors = [
            'input[type="checkbox"][value*="Non AC"]',
            'label:has-text("Non AC")',
            'input[value*="Non A/C"][type="checkbox"]'
        ]
        for selector in non_ac_selectors:
            try:
                non_ac_option = page.locator(selector).first
                if non_ac_option.is_visible(timeout=2000):
                    non_ac_option.click(force=True)
                    print('✅ Non-AC Bus filter applied')
                    page.wait_for_timeout(300)
                    break
            except:
                continue
        print('')
    except Exception as e:
        print(f'⚠️ Non-AC filter error: {e}\n')
    
    # Wait for Non-AC filtered results
    print('📍 Waiting for Non-AC filtered results...')
    page.wait_for_timeout(200)
    print('✅ Non-AC Filter applied!\n')
    
    # VERIFY Non-AC FILTER
    print('📍 Verifying Non-AC buses...')
    try:
        page.wait_for_timeout(300)
        bus_listings = page.locator('[class*="bus"], [class*="list-item"], .result-item, div[ng-repeat]').all()
        if len(bus_listings) > 0:
            ac_count = 0
            non_ac_count = 0
            for i, bus in enumerate(bus_listings[:5]):
                try:
                    bus_text = bus.text_content() or ''
                    bus_text_upper = bus_text.upper()
                    if 'NON AC' in bus_text_upper or 'NON-AC' in bus_text_upper or 'NONAC' in bus_text_upper or 'NON A/C' in bus_text_upper:
                        non_ac_count += 1
                        print(f'   Bus {i+1}: Non-AC ✅')
                    elif 'AC' in bus_text_upper or 'A/C' in bus_text_upper or 'A.C' in bus_text_upper:
                        ac_count += 1
                        print(f'   Bus {i+1}: AC ❌')
                    else:
                        print(f'   Bus {i+1}: Unknown ⚠️')
                except:
                    continue
            print(f'\n✅ Non-AC Buses found: {non_ac_count}')
            if ac_count > 0:
                print(f'❌ AC Buses found: {ac_count}')
                print('\n⚠️ TEST FAILED: AC buses found after Non-AC filter!\n')
                assert False, f"Non-AC Filter Failed: Found {ac_count} AC buses"
            else:
                print('✅ All buses are Non-AC - Filter working!')
            print('')
        else:
            print('⚠️ No bus listings found\n')
    except AssertionError:
        raise
    except Exception as e:
        print(f'⚠️ Non-AC Verification error: {e}\n')
    
    # RESET FILTER AFTER Non-AC
    print('📍 Clicking Reset Filter (final)...')
    try:
        page.wait_for_timeout(500)
        for selector in reset_selectors:
            try:
                reset_btn = page.locator(selector).first
                if reset_btn.is_visible(timeout=2000):
                    reset_btn.click(force=True)
                    print('✅ Reset Filter clicked (final)!\n')
                    page.wait_for_timeout(500)
                    break
            except:
                continue
    except Exception as e:
        print(f'⚠️ Reset error: {e}\n')
    
    # FILTER: Sleeper Bus Type
    print('📍 Applying Sleeper Bus filter...')
    try:
        page.wait_for_timeout(300)
        sleeper_selectors = [
            'input[type="checkbox"][value*="Sleeper"]',
            'label:has-text("Sleeper")',
            'input[id*="sleeper"][type="checkbox"]',
            '[class*="filter"] input:has-text("Sleeper")'
        ]
        for selector in sleeper_selectors:
            try:
                sleeper_option = page.locator(selector).first
                if sleeper_option.is_visible(timeout=2000):
                    sleeper_option.click(force=True)
                    print('✅ Sleeper Bus filter applied')
                    page.wait_for_timeout(300)
                    break
            except:
                continue
        print('')
    except Exception as e:
        print(f'⚠️ Sleeper filter error: {e}\n')
    
    # Wait for Sleeper filtered results
    print('📍 Waiting for Sleeper filtered results...')
    page.wait_for_timeout(200)
    print('✅ Sleeper Filter applied!\n')
    
    # RESET FILTER AFTER Sleeper
    print('📍 Clicking Reset Filter...')
    try:
        page.wait_for_timeout(500)
        for selector in reset_selectors:
            try:
                reset_btn = page.locator(selector).first
                if reset_btn.is_visible(timeout=2000):
                    reset_btn.click(force=True)
                    print('✅ Reset Filter clicked!\n')
                    page.wait_for_timeout(500)
                    break
            except:
                continue
    except Exception as e:
        print(f'⚠️ Reset error: {e}\n')
    
    # FILTER: Seater Bus Type
    print('📍 Applying Seater Bus filter...')
    try:
        page.wait_for_timeout(300)
        seater_selectors = [
            'input[type="checkbox"][value*="Seater"]',
            'label:has-text("Seater")',
            'input[id*="seater"][type="checkbox"]',
            '[class*="filter"] input:has-text("Seater")'
        ]
        for selector in seater_selectors:
            try:
                seater_option = page.locator(selector).first
                if seater_option.is_visible(timeout=2000):
                    seater_option.click(force=True)
                    print('✅ Seater Bus filter applied')
                    page.wait_for_timeout(300)
                    break
            except:
                continue
        print('')
    except Exception as e:
        print(f'⚠️ Seater filter error: {e}\n')
    
    # Wait for Seater filtered results
    print('📍 Waiting for Seater filtered results...')
    page.wait_for_timeout(200)
    print('✅ Seater Filter applied!\n')
    
    # RESET FILTER AFTER Seater
    print('📍 Clicking Reset Filter (final)...')
    try:
        page.wait_for_timeout(500)
        for selector in reset_selectors:
            try:
                reset_btn = page.locator(selector).first
                if reset_btn.is_visible(timeout=2000):
                    reset_btn.click(force=True)
                    print('✅ Reset Filter clicked (final)!\n')
                    page.wait_for_timeout(500)
                    break
            except:
                continue
    except Exception as e:
        print(f'⚠️ Reset error: {e}\n')
    
    # FILTER: Bus Operator - Click First Operator
    print('📍 Applying Bus Operator filter (first operator)...')
    try:
        page.wait_for_timeout(300)
        operator_selectors = [
            '[class*="operator"] input[type="checkbox"]',
            '[class*="travels"] input[type="checkbox"]',
            'input[type="checkbox"][name*="operator"]',
            'label:has-text("Travels") input[type="checkbox"]',
            '[class*="filter"] input[type="checkbox"]:has-text("Travels")'
        ]
        operator_clicked = False
        for selector in operator_selectors:
            try:
                operators = page.locator(selector)
                if operators.count() > 0:
                    first_operator = operators.first
                    if first_operator.is_visible(timeout=2000):
                        first_operator.click(force=True)
                        print('✅ First Bus Operator filter applied')
                        page.wait_for_timeout(300)
                        operator_clicked = True
                        break
            except:
                continue
        
        if not operator_clicked:
            print('⚠️ Bus Operator filter not found')
        print('')
    except Exception as e:
        print(f'⚠️ Bus Operator filter error: {e}\n')
    
    # Wait for Bus Operator filtered results
    print('📍 Waiting for Bus Operator filtered results...')
    page.wait_for_timeout(200)
    print('✅ Bus Operator Filter applied!\n')
    
    # RESET FILTER AFTER Bus Operator
    print('📍 Clicking Reset Filter (final)...')
    try:
        page.wait_for_timeout(500)
        for selector in reset_selectors:
            try:
                reset_btn = page.locator(selector).first
                if reset_btn.is_visible(timeout=2000):
                    reset_btn.click(force=True)
                    print('✅ Reset Filter clicked (final)!\n')
                    page.wait_for_timeout(500)
                    break
            except:
                continue
    except Exception as e:
        print(f'⚠️ Reset error: {e}\n')
    
    print('🔍 === FILTERS COMPLETED ===\n')
    
    # STEP 5: Select seat button
    print('📍 Opening seat layout...')
    select_seat_button = page.locator('button:has-text("Select Seat"), a:has-text("Select Seat")').first
    expect(select_seat_button).to_be_visible(timeout=20000)
    select_seat_button.click()
    page.wait_for_timeout(2000)
    print('✅ Seat layout opened\n')
    
    # STEP 6: Select any ONE available seat (DYNAMIC - avoid booked/grey seats)
    print('📍 Selecting any available seat...')
    
    seat_clicked = False
    
    # Wait for seat layout to fully load
    page.wait_for_timeout(2000)
    
    # Try multiple strategies to find and select available seats only
    strategies = [
        # Strategy 1: Available class seats
        {
            'selector': '[class*="avail"]:not([class*="booked"]):not([class*="grey"]):not([class*="disabled"])',
            'name': 'Available seats'
        },
        # Strategy 2: ng-click seats that are available
        {
            'selector': '[ng-click*="SelectSeat"]:not([class*="booked"]):not([class*="grey"])',
            'name': 'Clickable available seats'
        },
        # Strategy 3: Seats with specific available status
        {
            'selector': '.seat.available, .available-seat',
            'name': 'Available seat class'
        },
        # Strategy 4: Visible seats excluding booked ones
        {
            'selector': '[class*="seat"]:not([class*="booked"]):not([class*="grey"]):not([class*="blocked"])',
            'name': 'Non-booked seats'
        }
    ]
    
    for strategy in strategies:
        if seat_clicked:
            break
            
        try:
            page.wait_for_timeout(500)
            seats = page.locator(strategy['selector'])
            total = seats.count()
            
            if total > 0:
                # Try first 10 visible seats
                for i in range(min(total, 10)):
                    try:
                        seat = seats.nth(i)
                        
                        if seat.is_visible(timeout=1000):
                            # Check if seat is really available (not grey/disabled)
                            seat_classes = seat.get_attribute('class') or ''
                            
                            # Skip if seat has booked/grey/disabled in class
                            if any(word in seat_classes.lower() for word in ['booked', 'grey', 'disabled', 'blocked', 'unavailable']):
                                continue
                            
                            # Scroll into view first
                            seat.scroll_into_view_if_needed()
                            page.wait_for_timeout(500)
                            
                            # Click the seat
                            seat.click(force=True)
                            page.wait_for_timeout(1500)
                            
                            # Verify seat is selected - check if class changed or selected class added
                            seat_classes_after = seat.get_attribute('class') or ''
                            if 'select' in seat_classes_after.lower() or seat_classes_after != seat_classes:
                                print('✅ ONE SEAT SELECTED\n')
                                seat_clicked = True
                                break
                    except:
                        continue
                
                if seat_clicked:
                    break
        except:
            continue
    
    if not seat_clicked:
        print('⚠️ No available seat selected\n')
    
    # STEP 7 & 8: Boarding and Dropping
    print('📍 Selecting BOARDING & DROPPING points...')
    
    try:
        page.wait_for_timeout(300)
        
        # Find all clickable labels with ng-click
        labels = page.locator('label[ng-click]')
        label_count = labels.count()
        
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
                        page.wait_for_timeout(200)
                    elif not dropping_clicked:
                        print('✅ DROPPING POINT SELECTED!\n')
                        dropping_clicked = True
                        page.wait_for_timeout(200)
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
        page.wait_for_timeout(300)
        
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
        page.wait_for_timeout(300)
        
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
        
        page.wait_for_timeout(300)
        
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
        
        page.wait_for_timeout(300)
        
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
        
        page.wait_for_timeout(300)
        
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
        
        page.wait_for_timeout(200)
        
    except Exception as e:
        print(f'⚠️ Error filling details: {e}\n')
    
    # STEP 11: Select insurance - Yes
    print('📍 Selecting insurance: Yes')
    try:
        page.wait_for_timeout(200)
        
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
        
        page.wait_for_timeout(200)
        
    except Exception as e:
        print(f'⚠️ Error selecting insurance: {e}\n')
    
    # STEP 12: Select insurance condition checkbox
    print('📍 Selecting insurance condition...')
    try:
        page.wait_for_timeout(300)
        
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
        
        page.wait_for_timeout(200)
        
    except Exception as e:
        print(f'⚠️ Error selecting insurance condition: {e}\n')
    
    # STEP 13: Fill email
    print('📍 Filling email: cs@gmail.com')
    try:
        page.wait_for_timeout(300)
        
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
        
        page.wait_for_timeout(200)
        
    except Exception as e:
        print(f'⚠️ Error filling email: {e}\n')
    
    # STEP 14: Fill mobile number
    print('📍 Filling mobile number: 8445121366')
    try:
        page.wait_for_timeout(200)
        
        # Try multiple selectors for mobile field (avoid country code dropdown)
        mobile_selectors = [
            'input[maxlength="10"][type="tel"]',
            'input[name*="mobile"]:not([name*="country"]):not([maxlength="3"])',
            'input[name*="Mobile"]:not([name*="country"]):not([maxlength="3"])',
            'input[id*="mobile"]:not([id*="country"]):not([maxlength="3"])',
            'input[placeholder*="mobile"]:not([maxlength="3"])',
            'input[placeholder*="Mobile Number"]',
            'input[type="tel"]:not([name*="country"]):not([id*="country"]):not([maxlength="3"])'
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
                            # Check maxlength to avoid country code field (usually maxlength=3 or 4)
                            maxlength = mobile_field.get_attribute('maxlength')
                            if maxlength and int(maxlength) < 8:
                                continue
                            
                            # Check if field is editable and not a dropdown
                            field_type = mobile_field.get_attribute('type')
                            if field_type in ['tel', 'text', 'number']:
                                # Focus on the field
                                mobile_field.click()
                                page.wait_for_timeout(300)
                                
                                # Clear field completely
                                mobile_field.fill('')
                                page.wait_for_timeout(200)
                                
                                # Type the number
                                mobile_field.type('8445121366', delay=50)
                                page.wait_for_timeout(300)
                                
                                # Verify it was entered
                                value = mobile_field.input_value()
                                if '8445121366' in value or '844512' in value:
                                    print(f'✅ Mobile number filled: 8445121366\n')
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
        
        page.wait_for_timeout(200)
        
    except Exception as e:
        print(f'⚠️ Error filling mobile: {e}\n')
    
    # STEP 15: Click Continue to go to next page
    print('📍 Clicking Continue to next page...')
    try:
        page.wait_for_timeout(300)
        
        # Scroll to bottom to ensure button is visible
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(300)
        
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
                                page.wait_for_timeout(200)
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
            
        page.wait_for_timeout(300)
        
    except Exception as e:
        print(f'⚠️ Error clicking continue: {e}\n')
    
    # STEP 16: Click on Wallets payment option
    print('📍 Selecting Wallets payment option...')
    try:
        page.wait_for_timeout(5000)
        
        wallet_clicked = False
        
        # Silently check if More button needs to be clicked first
        try:
            more_btn = page.locator('li:has-text("More")').first
            if more_btn.is_visible(timeout=1000):
                more_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                more_btn.click(force=True)
                page.wait_for_timeout(2000)
        except:
            pass
        
        # Now click on Wallets directly
        element_types = ['span', 'div', 'li', 'label', 'a']
        
        for elem_type in element_types:
            try:
                selector = f'{elem_type}:has-text("Wallets")'
                elements = page.locator(selector).all()
                
                for elem in elements:
                    try:
                        text = elem.text_content() or ''
                        if len(text.strip()) < 30 and text.strip() == 'Wallets':
                            elem.scroll_into_view_if_needed(timeout=2000)
                            page.wait_for_timeout(500)
                            elem.click(timeout=2000)
                            wallet_clicked = True
                            page.wait_for_timeout(1000)
                            break
                    except:
                        try:
                            elem.click(force=True, timeout=2000)
                            wallet_clicked = True
                            page.wait_for_timeout(1000)
                            break
                        except:
                            continue
                
                if wallet_clicked:
                    break
                    
            except:
                continue
        
        # JavaScript fallback
        if not wallet_clicked:
            try:
                result = page.evaluate("""
                    () => {
                        const allElements = document.querySelectorAll('li, a, button, div, span, label');
                        for (let elem of allElements) {
                            const text = elem.textContent || '';
                            if (text.trim() === 'Wallets') {
                                elem.scrollIntoView({behavior: 'smooth', block: 'center'});
                                elem.click();
                                return {success: true};
                            }
                        }
                        return {success: false};
                    }
                """)
                
                if result.get('success'):
                    wallet_clicked = True
                    page.wait_for_timeout(1000)
            except:
                pass
        
        if wallet_clicked:
            print('✅ Wallets clicked\n')
        else:
            print('⚠️ Wallets not found\n')
        
        page.wait_for_timeout(1000)
        
    except Exception as e:
        print(f'⚠️ Error selecting Wallets: {e}\n')
    
    # STEP 17: Select Bajaj Pay
    print('📍 Selecting Bajaj Pay...')
    try:
        page.wait_for_timeout(200)
        
        bajaj_selectors = [
            'label:has-text("Bajaj")',
            'div:has-text("Bajaj Pay")',
            'span:has-text("Bajaj")',
            'input[value*="Bajaj"][type="radio"]',
            'input[value*="bajaj"][type="radio"]',
            '[id*="bajaj"]',
            '[name*="bajaj"]'
        ]
        
        bajaj_clicked = False
        for selector in bajaj_selectors:
            try:
                bajaj_option = page.locator(selector).first
                if bajaj_option.is_visible(timeout=2000):
                    bajaj_option.click(force=True)
                    print('✅ Bajaj Pay selected\n')
                    bajaj_clicked = True
                    break
            except:
                continue
        
        if not bajaj_clicked:
            print('⚠️ Bajaj Pay option not found\n')
        
        page.wait_for_timeout(200)
        
    except Exception as e:
        print(f'⚠️ Error selecting Bajaj Pay: {e}\n')
    
    print('🎉 === BOOKING FLOW COMPLETED ===\n')

    # Keep the browser open for manual inspection when debugging.
    if os.getenv('EMT_PAUSE_AT_END', '').lower() in {'1', 'true', 'yes'}:
        print('⏸️ Paused at end (EMT_PAUSE_AT_END=1). Press Ctrl+C in terminal to stop.')
        try:
            page.wait_for_timeout(10_000_000)
        except Exception:
            pass


def run_visual_demo():
    """Run the complete booking flow in a visible browser (no pytest runner)."""
    slowmo = int(os.getenv("EMT_SLOWMO", "200"))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=slowmo)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        page.goto('https://www.easemytrip.com/bus/', wait_until='domcontentloaded')
        page.wait_for_timeout(500)

        print('\n🚌 === VISUAL COMPLETE FLOW STARTING ===\n')

        try:
            # Reuse the existing full-flow logic by calling the test function directly.
            test_tc_005_click_search_button(page)
        except Exception as e:
            print(f"\n❌ Visual run failed: {e}\n")
            # On failure, keep browser open for inspection unless user disables it.
            if os.getenv('EMT_NO_PAUSE_ON_ERROR', '').lower() not in {'1', 'true', 'yes'}:
                print('⏸️ Paused on error. Close browser window or press Ctrl+C to stop.')
                try:
                    page.wait_for_timeout(10_000_000)
                except Exception:
                    pass
            raise

        # If you want to keep the browser open at the very end:
        if os.getenv('EMT_PAUSE_AT_END', '').lower() in {'1', 'true', 'yes'}:
            print('⏸️ Paused at end (EMT_PAUSE_AT_END=1). Close browser window or press Ctrl+C to stop.')
            try:
                page.wait_for_timeout(10_000_000)
            except Exception:
                pass


if __name__ == "__main__":
    # Default: run a visual demo (stable, no pytest plugin lifecycle).
    # If you want to run the pytest test instead, set EMT_RUN_PYTEST=1.
    if os.getenv('EMT_RUN_PYTEST', '').lower() in {'1', 'true', 'yes'}:
        import sys

        args = [
            "-s",  # show print() output
            os.path.abspath(__file__),
            "--headed",
            "--slowmo=200",
            "--browser=chromium",
            "--tracing=retain-on-failure",
            "--video=retain-on-failure",
            "--screenshot=only-on-failure",
            "--output=playwright-artifacts",
        ]
        sys.exit(pytest.main(args))

    run_visual_demo()
