import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
import time
import re


@pytest.fixture(scope="function")
def setup(page: Page):
    page.set_default_timeout(60000)
    page.goto('https://www.easemytrip.com/bus/', wait_until='domcontentloaded')
    expect(page).to_have_url(re.compile(r'.*easemytrip\.com/bus/.*'))
    page.wait_for_timeout(3000)
    yield page


def select_city(page: Page, input_selector: str, city_name: str):
    city_input = page.locator(input_selector)
    expect(city_input).to_be_visible()
    city_input.fill(city_name)
    page.wait_for_selector('.auto-sugg-pre ul li', state='visible')
    page.locator(f'.auto-sugg-pre ul li:has-text("{city_name}")').first.click()
    page.wait_for_timeout(1000)


def test_tc_005_click_search_button(setup):
    page = setup
    
    select_city(page, '#txtSrcCity', 'Delhi')
    page.wait_for_timeout(2000)
    
    select_city(page, '#txtDesCity', 'Jaipur')
    page.wait_for_timeout(2000)
    
    date_picker = page.locator('#datepicker')
    expect(date_picker).to_be_visible()
    date_picker.click()
    page.wait_for_timeout(2000)
    
    page.wait_for_selector('.ui-datepicker-calendar', state='visible', timeout=5000)
    
    day = 31
    date_element = page.locator(f'.ui-datepicker-calendar .ui-state-default:has-text("{day}")').first
    date_element.click(force=True)
    page.wait_for_timeout(2000)
    
    search_button = page.locator('#srcbtn')
    expect(search_button).to_be_visible()
    search_button.click()
    page.wait_for_url(re.compile(r'.*easemytrip\.com/home/list.*'), timeout=60000)
    page.wait_for_timeout(3000)
    
    try:
        page.wait_for_timeout(1000)
        ac_selectors = [
            'input[type="checkbox"][value*="AC"]',
            'label:has-text("AC")',
            'input[value*="A/C"][type="checkbox"]'
        ]
        for selector in ac_selectors:
            try:
                ac_option = page.locator(selector).first
                if ac_option.is_visible(timeout=2000):
                    ac_option.click(force=True)
                    page.wait_for_timeout(1000)
                    break
            except:
                continue
    except:
        pass
    
    try:
        page.wait_for_timeout(1000)
        reset_selectors = ['button:has-text("Reset")', 'a:has-text("Reset")']
        for selector in reset_selectors:
            try:
                reset_btn = page.locator(selector).first
                if reset_btn.is_visible(timeout=2000):
                    reset_btn.click(force=True)
                    page.wait_for_timeout(1000)
                    break
            except:
                continue
    except:
        pass
    
    select_seat_button = page.locator('button:has-text("Select Seat"), a:has-text("Select Seat")').first
    expect(select_seat_button).to_be_visible(timeout=20000)
    select_seat_button.click()
    page.wait_for_timeout(3000)
    
    seat_clicked = False
    strategies = [
        '[class*="avail"]:not([class*="booked"]):not([class*="grey"])',
        '[ng-click*="SelectSeat"]:not([class*="booked"])',
        '.seat.available',
        '[class*="seat"]:not([class*="booked"]):not([class*="grey"])'
    ]
    
    for strategy in strategies:
        if seat_clicked:
            break
        try:
            page.wait_for_timeout(1000)
            seats = page.locator(strategy)
            total = seats.count()
            if total > 0:
                for i in range(min(total, 5)):
                    try:
                        seat = seats.nth(i)
                        if seat.is_visible(timeout=1000):
                            seat_classes = seat.get_attribute('class') or ''
                            if any(word in seat_classes.lower() for word in ['booked', 'grey', 'disabled']):
                                continue
                            seat.click(force=True)
                            page.wait_for_timeout(1500)
                            seat_clicked = True
                            break
                    except:
                        continue
        except:
            continue
    
    try:
        page.wait_for_timeout(1000)
        labels = page.locator('label[ng-click]')
        label_count = labels.count()
        boarding_clicked = False
        dropping_clicked = False
        for i in range(label_count):
            if boarding_clicked and dropping_clicked:
                break
            label = labels.nth(i)
            try:
                if label.is_visible():
                    label.click(force=True)
                    if not boarding_clicked:
                        boarding_clicked = True
                        page.wait_for_timeout(500)
                    elif not dropping_clicked:
                        dropping_clicked = True
                        page.wait_for_timeout(500)
                        break
            except:
                continue
    except:
        pass
    
    try:
        page.wait_for_timeout(3000)
        continue_selectors = [
            'button:has-text("Continue")',
            'a:has-text("Continue")',
            'input[value="Continue"]'
        ]
        for selector in continue_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    btn.click(force=True)
                    page.wait_for_timeout(5000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    break
            except:
                continue
    except:
        pass
    
    try:
        page.wait_for_timeout(3000)
        title_selectors = ['select[name*="title"]', 'select[id*="title"]']
        for selector in title_selectors:
            try:
                title_dropdown = page.locator(selector).first
                if title_dropdown.is_visible(timeout=2000):
                    title_dropdown.select_option(label='Mr')
                    break
            except:
                continue
        
        page.wait_for_timeout(1000)
        fname_selectors = ['input[name*="firstName"]', 'input[id*="firstName"]']
        for selector in fname_selectors:
            try:
                fname_field = page.locator(selector).first
                if fname_field.is_visible(timeout=2000):
                    fname_field.fill('test')
                    break
            except:
                continue
        
        page.wait_for_timeout(1000)
        lname_selectors = ['input[name*="lastName"]', 'input[id*="lastName"]']
        for selector in lname_selectors:
            try:
                lname_field = page.locator(selector).first
                if lname_field.is_visible(timeout=2000):
                    lname_field.fill('test')
                    break
            except:
                continue
        
        page.wait_for_timeout(1000)
        age_selectors = ['input[name*="age"]', 'input[id*="age"]']
        for selector in age_selectors:
            try:
                age_field = page.locator(selector).first
                if age_field.is_visible(timeout=2000):
                    age_field.fill('25')
                    break
            except:
                continue
        
        page.wait_for_timeout(2000)
    except:
        pass
    
    try:
        page.wait_for_timeout(2000)
        insurance_selectors = [
            'input[value="yes"][type="radio"]',
            'input[value="Yes"][type="radio"]',
            'label:has-text("Yes")'
        ]
        for selector in insurance_selectors:
            try:
                insurance_option = page.locator(selector).first
                if insurance_option.is_visible(timeout=2000):
                    insurance_option.click(force=True)
                    break
            except:
                continue
        page.wait_for_timeout(2000)
    except:
        pass
    
    try:
        page.wait_for_timeout(1000)
        condition_selectors = [
            'input[type="checkbox"][name*="insurance"]',
            'input[type="checkbox"][id*="insurance"]'
        ]
        for selector in condition_selectors:
            try:
                checkbox = page.locator(selector).first
                if checkbox.is_visible(timeout=2000):
                    checkbox.check(force=True)
                    break
            except:
                continue
        page.wait_for_timeout(2000)
    except:
        pass
    
    try:
        page.wait_for_timeout(1000)
        email_selectors = ['input[type="email"]', 'input[name*="email"]']
        for selector in email_selectors:
            try:
                email_field = page.locator(selector).first
                if email_field.is_visible(timeout=2000):
                    email_field.fill('cs@gmail.com')
                    break
            except:
                continue
        page.wait_for_timeout(2000)
    except:
        pass
    
    try:
        page.wait_for_timeout(2000)
        mobile_selectors = [
            'input[maxlength="10"][type="tel"]',
            'input[name*="mobile"]:not([maxlength="3"])',
            'input[type="tel"]:not([maxlength="3"])'
        ]
        for selector in mobile_selectors:
            try:
                mobile_field = page.locator(selector).first
                if mobile_field.is_visible(timeout=1000):
                    maxlength = mobile_field.get_attribute('maxlength')
                    if maxlength and int(maxlength) < 8:
                        continue
                    mobile_field.click()
                    page.wait_for_timeout(300)
                    mobile_field.fill('')
                    page.wait_for_timeout(200)
                    mobile_field.type('8445121366', delay=50)
                    page.wait_for_timeout(1000)
                    break
            except:
                continue
        page.wait_for_timeout(2000)
    except:
        pass
    
    try:
        page.wait_for_timeout(3000)
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.wait_for_timeout(1000)
        continue_selectors = [
            'button:has-text("Continue")',
            'a:has-text("Continue")',
            'button:has-text("Proceed")'
        ]
        for selector in continue_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1000):
                    btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    btn.click(force=True)
                    page.wait_for_timeout(5000)
                    page.wait_for_load_state('domcontentloaded', timeout=30000)
                    break
            except:
                continue
        page.wait_for_timeout(3000)
    except:
        pass
    
    try:
        page.wait_for_timeout(5000)
        page.evaluate('window.scrollTo(0, 0)')
        page.wait_for_timeout(300)
        page.evaluate('window.scrollBy(0, 400)')
        page.wait_for_timeout(200)
        
        try:
            wallet_element = page.get_by_role('listitem').filter(has_text='Wallet').first
            if wallet_element:
                wallet_element.click(force=True, timeout=3000)
                page.wait_for_timeout(200)
        except:
            pass
        page.wait_for_timeout(200)
    except:
        pass
    
    try:
        page.wait_for_timeout(200)
        bajaj_selectors = [
            'label:has-text("Bajaj")',
            'div:has-text("Bajaj Pay")',
            'input[value*="Bajaj"][type="radio"]'
        ]
        for selector in bajaj_selectors:
            try:
                bajaj_option = page.locator(selector).first
                if bajaj_option.is_visible(timeout=2000):
                    bajaj_option.click(force=True)
                    break
            except:
                continue
        page.wait_for_timeout(200)
    except:
        pass
