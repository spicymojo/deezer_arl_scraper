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
app = Flask(__name__, template_folder='resources')
socketio = SocketIO(app, async_mode='threading')

# --- Default Credentials ---
DEFAULT_EMAIL = "giloalfano0@gmail.com"
DEFAULT_PASSWORD = "A260219735364g"


def get_arl_cookie(email, password):
    driver = None
    try:
        socketio.emit('status', {'msg': 'Initializing Chrome browser in headless mode...'})

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("window-size=1280,800")

        # --- MODIFICATION FOR RASPBERRY PI ---
        # When running on the Pi, Selenium finds the system-installed driver automatically.
        driver_path = './resources/chromedriver.exe' if sys.platform == 'win32' else '/usr/bin/chromedriver'

        if os.path.exists(driver_path):
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Fallback for systems where driver is in PATH but not at the explicit Pi path
            socketio.emit('status', {'msg': 'Driver not found at specific path, trying default PATH...'})
            driver = webdriver.Chrome(options=chrome_options)

        wait = WebDriverWait(driver, 30)  # Increased timeout for Raspberry Pi

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
        # ... (error handling)
    except Exception as e:
        socketio.emit('status', {'msg': f'❌ An unexpected error occurred: {e}'})
    finally:
        if driver:
            driver.quit()
            socketio.emit('status', {'msg': 'Browser closed. Process finished.'})


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('start_scraping')
def handle_start_scraping(json):
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
    # On Pi, you might access it from another computer on the network
    print("Starting server at http://0.0.0.0:5000")
    # webbrowser.open_new("http://127.0.0.1:5000")

    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
