import json
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def setup_chrome_options():
    """Configure Chrome options to better mimic a real browser"""
    options = Options()

    # Basic options
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    # Anti-detection options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Cookie and security options
    options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-site-isolation-trials")

    # Basic options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--start-maximized")

    # Anti-detection options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Cookie and security options
    options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-site-isolation-trials")

    # User agent
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    return options


async def prp_data_fetch(email: str, password: str):
    # Step 1: Setup Chrome
    options = setup_chrome_options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Hide webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        print("🚀 Starting correct authentication flow...")

        # Step 1: Land on ehaj homepage and wait for initial cookie
        print("🏠 Step 1: Landing on https://ehaj.hajj.gov.bd/")
        driver.get("https://ehaj.hajj.gov.bd/")

        # Step 2: Find and click login button
        print("🔍 Step 2: Looking for login button...")
        time.sleep(2)
        login_selectors = [
            '//a[contains(text(), "লগইন")]',
            '//a[@href and contains(@href, "openid-connect/auth")]',
            '//a[@href and contains(@href, "client_id=e-hajj")]',
            'a[href*="client_id=e-hajj"]',
            '.nav-link[href*="openid-connect"]'
        ]

        login_element = None
        for selector in login_selectors:
            try:
                if selector.startswith('//'):
                    login_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    login_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                print(f"✅ Found login button with selector: {selector}")
                break
            except:
                continue

        if not login_element:
            print("❌ Could not find login button")
            print("Available links:")
            links = driver.find_elements(By.TAG_NAME, "a")
            for i, link in enumerate(links[:10]):
                href = link.get_attribute("href")
                text = link.text.strip()[:50]
                print(f"  {i + 1}. '{text}' -> {href}")
            return False

        print("🖱️ Clicking login button...")
        login_href = login_element.get_attribute("href")
        print(f"Login URL: {login_href}")

        driver.execute_script("arguments[0].click();", login_element)

        # Step 3: Wait for redirect to keycloak auth page
        print("⏳ Step 3: Waiting for redirect to keycloak...")
        time.sleep(2)
        WebDriverWait(driver, 15).until(
            lambda d: "idp.hajj.gov.bd" in d.current_url and "openid-connect/auth" in d.current_url
        )

        # Step 4: Find and click the "অফিস/সংস্থা/ব্যাংক/হজ এজেন্সি লগইন" button
        print("🔍 Step 4: Looking for PRP login button...")

        prp_login_selectors = [
            '#social-prp',
            '//a[@id="social-prp"]',
            '//a[contains(@href, "/broker/prp/login")]',
            '//a[contains(text(), "অফিস/সংস্থা/ব্যাংক/হজ এজেন্সি")]',
            'a[href*="/broker/prp/login"]',
            '.kc-social-item[href*="prp"]'
        ]

        prp_login_element = None
        for selector in prp_login_selectors:
            try:
                if selector.startswith('//'):
                    prp_login_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    prp_login_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                print(f"✅ Found PRP login button with selector: {selector}")
                break
            except:
                continue

        if not prp_login_element:
            print("❌ Could not find PRP login button")
            print("Available social login buttons:")
            social_buttons = driver.find_elements(By.CSS_SELECTOR, "a[class*='social'], a[id*='social']")
            for i, button in enumerate(social_buttons):
                href = button.get_attribute("href")
                text = button.text.strip()
                id_attr = button.get_attribute("id")
                print(f"  {i + 1}. ID: {id_attr}, Text: '{text}', Href: {href}")
            return False

        print("🖱️ Clicking PRP login button...")
        prp_href = prp_login_element.get_attribute("href")
        print(f"PRP login URL: {prp_href}")

        driver.execute_script("arguments[0].click();", prp_login_element)

        # Step 5: Wait for redirect to SSO login page
        print("⏳ Step 5: Waiting for redirect to SSO...")
        time.sleep(2)
        WebDriverWait(driver, 15).until(
            lambda d: "sso.hajj.gov.bd" in d.current_url
        )

        # Step 6: Enter email/username
        print("📝 Step 6: Entering username...")
        username_field = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        username_field.clear()
        username_field.send_keys(email)
        time.sleep(2)

        # Step 7: Click next button
        print("👆 Step 7: Clicking next button...")
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "next_btn"))
        )
        driver.execute_script("arguments[0].click();", next_btn)

        # Wait for password page to load
        time.sleep(3)

        # Step 8: Enter password
        print("🔑 Step 8: Entering password...")
        password_field = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(2)

        # Step 9: Click login button
        print("🚪 Step 9: Clicking login button...")
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login_btn"))
        )
        driver.execute_script("arguments[0].click();", login_btn)

        # Step 10: Wait for redirect back to ehaj dashboard
        print("⏳ Step 10: Waiting for redirect to ehaj dashboard...")

        redirect_success = False
        for attempt in range(2):  # Increased attempts for complex redirects
            current_url = driver.current_url
            print(f"Redirect check {attempt + 1}: {current_url}")

            if "ehaj.hajj.gov.bd/dashboard" in current_url:
                redirect_success = True
                print("✅ Successfully reached ehaj dashboard!")
                break
            elif "error" in current_url.lower():
                print("❌ Error detected in URL")
                break

            time.sleep(2)

        if not redirect_success:
            print(f"❌ Failed to reach dashboard. Final URL: {driver.current_url}")
            # Save debug info
            driver.save_screenshot("redirect_failed.png")
            with open("redirect_failed_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return False

        # Step 12: Now look for PRP login button on dashboard
        print("🔍 Step 12: Looking for PRP login on dashboard...")

        # Wait for page to fully load
        time.sleep(5)

        prp_dashboard_selectors = [
            '//a[contains(@href, "prp.pilgrimdb.org")]',
            '//a[contains(@href, "client_id=prp")]',
            '//a[contains(text(), "PRP LOGIN")]',
            '//a[contains(text(), "প্রাক নিবন্ধন")]',
            'a[href*="prp.pilgrimdb.org"]',
            'a[href*="client_id=prp"]'
        ]

        prp_dashboard_element = None
        for selector in prp_dashboard_selectors:
            try:
                if selector.startswith('//'):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    href = element.get_attribute("href")
                    if href and ("prp" in href.lower() or "client_id=prp" in href):
                        prp_dashboard_element = element
                        print(f"✅ Found PRP dashboard link: {href}")
                        break

                if prp_dashboard_element:
                    break

            except Exception as e:
                continue

        if not prp_dashboard_element:
            print("❌ Could not find PRP dashboard link")
            # Show available links for debugging
            links = driver.find_elements(By.TAG_NAME, "a")
            print("Available links on dashboard:")
            for i, link in enumerate(links[:15]):
                href = link.get_attribute("href")
                text = link.text.strip()[:50]
                if href:
                    print(f"  {i + 1}. '{text}' -> {href}")
            return False

        # Step 13: Click PRP login to go to PRP dashboard
        print(" Step 13: Navigating to PRP dashboard...")
        prp_dashboard_href = prp_dashboard_element.get_attribute("href")

        # Navigate to PRP dashboard
        driver.get(prp_dashboard_href)

        # Step 14: Wait for PRP dashboard and check cookies
        print("Step 14: Waiting for PRP dashboard to load...")

        WebDriverWait(driver, 30).until(
            lambda d: "prp.pilgrimdb.org" in d.current_url
        )

        # Step 15: Extract cookies from browser session
        print("Step 15: Extracting cookies from browser...")

        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        print(" Cookies extracted:")
        for name, value in cookie_dict.items():
            print(f"{name} = {value}")

        # Optionally: format into a single Cookie header string
        cookie_header = "; ".join([f"{name}={value}" for name, value in cookie_dict.items()])


        # Save cookies to file for later use
        with open("prp_cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)

        # Example: reuse cookies with requests
        session = requests.Session()
        for c in cookies:
            session.cookies.set(c['name'], c['value'])

        # registered data fetch
        url = "https://prp.pilgrimdb.org/registration/application/get-eligible-pilgrim-list"
        resp = session.post(url, data={"example": "value"})

        json_data = resp.json()
        registered_pilgrim = []

        for row in json_data.get("data", []):
            pilgrim_dict = {
                "tracking_id": row.get("tracking_no"),
                "passport_no": row.get("passport_no"),
                "passport_expiry_date": row.get("pass_exp_date"),
                "payment_status": row.get("payment_status_name"),
            }
            registered_pilgrim.append(pilgrim_dict)

        # Save to JSON file
        # with open("registered_pilgrim.json", "w", encoding="utf-8") as f:
        #     json.dump(registered_pilgrim, f, ensure_ascii=False, indent=4)
        print(f"{len(registered_pilgrim)} registered pilgrim saved successfully")

        # Now you can call authenticated APIs
        test_url = "https://prp.pilgrimdb.org/pilgrim/get-row-details-data"
        resp = session.post(test_url, data={"example": "value"})

        json_data = resp.json()
        app_data = []

        for row in json_data.get("data", []):
            try:
                # Parse the "action" link
                action_html = row.get("action")
                soup = BeautifulSoup(action_html, "html.parser")
                link = soup.find("a")["href"]

                # Visit the detail page
                detail_resp = session.get(link)
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

                serial_no_html = row.get("serial_no")
                serial_no_text = BeautifulSoup(serial_no_html, "html.parser").get_text(strip=True)
                tracking_id = row.get("tracking_no")

                # -- Extract collapseOne info --
                collapse_div = detail_soup.select_one("#collapseOne")
                data = {}
                if collapse_div:
                    strong_tags = collapse_div.find_all("strong")
                    for tag in strong_tags:
                        label = tag.get_text(strip=True).replace(":", "")
                        value = tag.next_sibling
                        if value:
                            value = value.strip()
                        else:
                            next_elem = tag.find_next_sibling(text=True)
                            value = next_elem.strip() if next_elem else None
                        data[label] = value

                # Build record
                app_data.append({
                    "Name (Bengali)": data.get("Name in Bengali"),
                    "Name (English)": row.get("full_name_english"),
                    "Father's Name": data.get("Father's Name"),
                    "Spouse Name": data.get("Spouse Name"),
                    "Occupation": data.get("Occupation"),
                    "NID": data.get("National ID"),
                    "Voucher": data.get("Pre-reg voucher"),
                    "Type": data.get("Type"),
                    "Listed In": data.get("Listed In"),
                    "Mother Name": data.get("Mother Name"),
                    "Date of Birth": data.get("Date of Birth"),
                    "Gender": data.get("Gender"),
                    "Management": data.get("Management"),
                    "Mobile": data.get("Mobile"),
                    "Passport Address": data.get("Passport Address"),
                    "Present Address": data.get("Present Address"),
                    "Permanent Address": data.get("Permanent Address"),
                    "Tracking ID": tracking_id,
                    "Serial No": serial_no_text,
                    "Group Name": row.get("group_name"),
                    "Payment Status": row.get("payment_status")
                })
                # with open("pilgrim_data.json", "w", encoding="utf-8") as f:
                #     json.dump(app_data, f, ensure_ascii=False, indent=2)

            except Exception as e:
                raise
        print(f"{len(app_data)} pre registered data fetched successfully")

        return registered_pilgrim, app_data

    except Exception as e:
        print(e)
