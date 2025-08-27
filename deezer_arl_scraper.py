import sys
import getpass
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

DEFAULT_EMAIL = ""
DEFAULT_PASSWORD = ""

print("Please enter your Deezer credentials.")
email_input = input("Email: ")
password_input = getpass.getpass("Password (input hidden): ")

email = email_input if email_input else (DEFAULT_EMAIL if DEFAULT_EMAIL else "")
password = password_input if password_input else (DEFAULT_PASSWORD if DEFAULT_PASSWORD else "")

if not email or not password:
    print("\nError: Email and password are required.")
    sys.exit(1)

# --- Selenium Automation ---
print("\nInitializing browser...")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)

try:
    print("Navigating to Deezer...")
    driver.get("https://www.deezer.com/us/login")

    try:
        print("Looking for GDPR consent button...")
        gdpr_button = wait.until(EC.element_to_be_clickable((By.ID, "gdpr-btn-accept-all")))
        print("Accepting GDPR consent...")
        gdpr_button.click()
    except TimeoutException:
        print("GDPR consent button not found or already accepted, continuing...")

    print("Waiting for login form to be available...")
    email_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='email-field']")))

    print(f"Logging in...")

    email_field.send_keys(email)
    time.sleep(random.uniform(0.5, 1.2))

    driver.find_element(By.CSS_SELECTOR, "[data-testid='password-field']").send_keys(password)
    time.sleep(random.uniform(0.3, 0.8))

    print("Waiting for login button to be clickable...")
    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='login-button']")))
    login_button.click()

    print("Waiting for login to complete...")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='section_title']")))
    print("✅ Login successful!")

    print("Extracting arl cookie...")
    all_cookies = driver.get_cookies()
    arl_cookie = next((cookie['value'] for cookie in all_cookies if cookie['name'] == 'arl'), None)

    if arl_cookie:
        print("\n--- Success! ---")
        print(f"Your Deezer arl cookie is:")
        print(arl_cookie)
    else:
        print("\n--- Error ---")
        print("Login appeared successful, but the 'arl' cookie could not be found.")

except TimeoutException:
    print("\n--- Error ---")
    print("A timeout occurred. The script failed to log in.")
    try:
        screenshot_path = "debug_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"A screenshot of the failure has been saved to: {screenshot_path}")
    except Exception as e:
        print(f"Could not save screenshot: {e}")

except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")

finally:
    print("\nClosing browser.")
    driver.quit()