import os
import sys
import time
import random
import webbrowser
from threading import Thread
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

# --- Flask and SocketIO Setup ---
# Tell Flask to look for templates in the 'resources' folder
app = Flask(__name__, template_folder='resources')
socketio = SocketIO(app, async_mode='threading')

# --- Default Credentials (Dev Feature) ---
# If the form fields are empty, these values will be used.
DEFAULT_EMAIL = ""
DEFAULT_PASSWORD = ""


def get_arl_cookie(email, password):
    """
    Automates Deezer login using a manually specified chromedriver.
    Sends status updates back to the web client via SocketIO.
    """
    driver = None
    try:
        socketio.emit('status', {'msg': 'Initializing Chrome browser in headless mode...'})

        # --- MODIFICATION: Configure Chrome for headless operation ---
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("window-size=1280,800")  # Set a window size to avoid responsive issues

        # Use the chromedriver.exe from the 'resources' folder
        service = ChromeService(executable_path='./resources/chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 25)

        socketio.emit('status', {'msg': 'Navigating to Deezer...'})
        driver.get("https://www.deezer.com/us/login")

        try:
            socketio.emit('status', {'msg': 'Looking for GDPR consent button...'})
            gdpr_button = wait.until(EC.element_to_be_clickable((By.ID, "gdpr-btn-accept-all")))
            socketio.emit('status', {'msg': 'Accepting GDPR consent...'})
            gdpr_button.click()
        except TimeoutException:
            socketio.emit('status', {'msg': 'GDPR consent button not found, continuing...'})

        socketio.emit('status', {'msg': 'Waiting for login form...'})
        email_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='email-field']")))

        socketio.emit('status', {'msg': 'Logging in...'})
        email_field.send_keys(email)
        time.sleep(random.uniform(0.5, 1.2))
        driver.find_element(By.CSS_SELECTOR, "[data-testid='password-field']").send_keys(password)
        time.sleep(random.uniform(0.3, 0.8))

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='login-button']")))
        login_button.click()

        socketio.emit('status', {'msg': 'Waiting for login to complete...'})
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='section_title']")))
        socketio.emit('status', {'msg': '✅ Login successful!'})

        socketio.emit('status', {'msg': 'Extracting arl cookie...'})
        all_cookies = driver.get_cookies()
        arl_cookie = next((cookie['value'] for cookie in all_cookies if cookie['name'] == 'arl'), None)

        if arl_cookie:
            socketio.emit('result', {'arl': arl_cookie})
        else:
            socketio.emit('status', {'msg': '❌ Error: Login successful, but could not find arl cookie.'})

    except TimeoutException:
        socketio.emit('status', {'msg': '❌ Error: A timeout occurred. Please check credentials and network.'})
        try:
            screenshot_path = "debug_screenshot.png"
            if driver:
                driver.save_screenshot(screenshot_path)
                socketio.emit('status', {'msg': f'A screenshot was saved to {screenshot_path}'})
        except Exception as e:
            socketio.emit('status', {'msg': f'Could not save screenshot: {e}'})
    except Exception as e:
        socketio.emit('status', {'msg': f'❌ An unexpected error occurred: {e}'})
    finally:
        if driver:
            driver.quit()
            socketio.emit('status', {'msg': 'Browser closed. Process finished.'})


@app.route('/')
def index():
    """Render the main web page."""
    return render_template('index.html')


@socketio.on('start_scraping')
def handle_start_scraping(json):
    """Handle the start event from the client."""
    email = json.get('email') or DEFAULT_EMAIL
    password = json.get('password') or DEFAULT_PASSWORD

    if not email or not password:
        socketio.emit('status', {'msg': 'Email and password are required as no defaults are set.'})
        return

    thread = Thread(target=get_arl_cookie, args=(email, password))
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    print("--- Deezer ARL Extractor Web App ---")
    print("Starting server at http://12.0.0.1:5000")
    print("Open this URL in your browser.")

    webbrowser.open_new("http://127.0.0.1:5000")

    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)