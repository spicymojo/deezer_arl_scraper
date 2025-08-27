# Deezer `arl` Cookie Extractor

This script automates the process of logging into a Deezer account to extract the `arl` session cookie. This cookie is often required for other applications or APIs that interact with Deezer services on your behalf.

The script uses Selenium to control a real web browser, ensuring it can handle modern web technologies like JavaScript, popups, and dynamic content.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python:** Version 3.8 or newer is recommended.
2.  **Google Chrome:** The script is configured to use Chrome, so you must have it installed.
3.  **A Deezer Account:** You will need valid Deezer login credentials.

## Setup Instructions

It is highly recommended to use a Python virtual environment to keep project dependencies isolated.

1.  **Clone the repository:**
    Download all the project files onto your local machine.

2.  **Create and Activate a Virtual Environment:**
    Open a terminal in your project folder and run:
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    With your virtual environment active, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1.  **Run the Script:**
    Execute the script from your terminal:
    ```bash
    python deezer_arl_scraper.py
    ```

2.  **Enter Credentials:**
    The script will prompt you to enter your Deezer email and password. The password input will be hidden for security.
    ```
    Please enter your Deezer credentials.
    Email: your_email@example.com
    Password (input hidden):
    ```

3.  **Automation:**
    A Chrome browser window will open and automatically perform the following steps:
    * Navigate to the Deezer login page.
    * Accept any GDPR/cookie consent popups.
    * Enter your credentials and submit the form.
    * Wait for the main page to load to confirm a successful login.

4.  **Get the Cookie:**
    If the login is successful, the script will print the `arl` cookie to your terminal and then close the browser.
    ```
    --- Success! ---
    Your Deezer arl cookie is:
    [a long string of characters will be printed here]
    ```

## Developer Feature (For Testing)

For faster testing, you can hardcode your credentials directly into the script.

* **How:** Open the script file and edit the `DEFAULT_EMAIL` and `DEFAULT_PASSWORD` variables at the top.
* **Usage:** When you run the script, simply press `Enter` at the email and password prompts to use the hardcoded values.
* **Security Warning:** This is a security risk. Never commit a file with your credentials to a public repository like GitHub. This feature is intended for local testing only.

## Troubleshooting

* **Timeout Error:** If the script fails with a timeout error, it will automatically save a `debug_screenshot.png` file. **Check this image first.** It will show you exactly what the browser was seeing at the moment of failure (e.g., an incorrect password error, a new popup, a CAPTCHA, etc.).
* **Script Stops Working:** Websites like Deezer frequently update their design. If this script suddenly stops working, it is likely because the HTML structure of the login page has changed. You will need to use your browser's Developer Tools (F12) to find the new `data-testid` or other selectors for the input fields and buttons, and then update them in the script.
