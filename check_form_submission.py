import json
import threading
import requests
import time
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv
import os

import undetected_chromedriver as uc

# load environment variables from .env file
load_dotenv()

def fill_input_field(driver, locator_type, locator_value, text):
    """Reusable function to locate an input field and send text."""
    input_field = driver.find_element(locator_type, locator_value)
    input_field.send_keys(text)

def click_element(driver, locator_type, locator_value):
    """Reusable function to locate and click an element."""
    # button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((locator_type, locator_value))
    # )
    button = driver.find_element(locator_type, locator_value)
    button.click()

def simulate_human_typing(input_element, text, delay=0.1):
    """Type text into an input element key-by-key with a delay."""
    for char in text:
        input_element.send_keys(char)
        time.sleep(delay)

def login_and_navigate():
    """Performs login for user while simulating human typing"""
    driver = webdriver.Chrome()

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    try:
        # Open login page
        print("Opening login page...")
        driver.get("https://www.anthem.com/ca/login/")

        # Fill in credentials
        print("Filling in username...")
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtUsername"))
        )
        simulate_human_typing(username_input, username, delay=0.2)

        print("Filling in password...")
        password_input = driver.find_element(By.ID, "txtPassword")
        simulate_human_typing(password_input, password, delay=0.2)

        # Click login button
        print("Clicking login button...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnLogin"))
        )
        login_button.click()

        # Wait for the next page to load
        print("Waiting for dashboard...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboardElement"))
        )
        print("Login successful and page loaded!")

    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Quitting driver...")
        driver.quit()

def save_cookies(driver, filepath):
    """Saves cookies from Chrome profile user session."""
    # store session details in a pickled file
    cookies = driver.get_cookies()
    with open(filepath, "wb") as file:
        pickle.dump(cookies, file)
        print("Cookies saved!")

def filter_cookies(cookies):
    essential_cookie_names = {
        "SMSESSION",
        "mod_auth_openidc_session",
        "mod_auth_openidc_state_*",
        "pfrememberme",
        "lsid", 
        "target"
    }
    filtered_cookies = [
        cookie for cookie in cookies if any(cookie["name"].startswith(name) for name in essential_cookie_names)
    ]

    return filtered_cookies

def load_cookies(driver, filepath):
    """Loads cookies from a file to a browser sessions."""
    with open(filepath, "rb") as file:
        cookies = pickle.load(file)
        for cookie in filter_cookies(cookies):
            driver.add_cookie(cookie)
        print("Cookies loaded!")

def locate_and_click(driver, element_id, timeout=10):
    """Locates and clicks the button specified."""
    if is_error_present(driver):
        print("Error detected before attempting to click.")
        return False
    try:
        # Locate the element
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        print(f"Element with ID '{element_id}' located!")

        # Optional: Wait for stabilization (if necessary)
        time.sleep(2)

        # Click the element using JavaScript
        driver.execute_script("arguments[0].click();", element)
        print(f"Clicked the element with ID '{element_id}' using JavaScript!")
    except Exception as e:
        print(f"Failed to click the element with ID '{element_id}': {e}")

def is_error_present(driver, timeout=20):
    """Wait for the error message to appear and check if it is displayed."""
    try:
        # Wait until the error container is present and visible
        error_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ant-error-container"))
        )
        # Optional: Check the text content if needed
        if "Sorry, looks like something isn't working." in error_element.text:
            return True
    except:
        return False
    
def check_form_submission(driver):
    """Function to automate form submission and intercept the form request using CDP."""

    intercepted_requests = []  # To store intercepted requests

    # Enable Fetch domain and set request interception patterns
    driver.execute_cdp_cmd("Fetch.enable", {"patterns": [{"urlPattern": "*new-message*", "requestStage": "Request"}]})

    def handle_request():
        while True:
            try:
                events = driver.execute_cdp_cmd("Fetch.takePausedRequest", {})
                if events and "new-message" in events["request"]["url"]:
                    print(f"Intercepted request to: {events['request']['url']}")
                    intercepted_requests.append(events)
                    driver.execute_cdp_cmd("Fetch.failRequest", {"requestId": events["requestId"], "errorReason": "BlockedByClient"})
                    break
            except Exception:
                pass  # Ignore if no requests are paused

    threading.Thread(target=handle_request, daemon=True).start()


    try: 
        # Refresh page to apply cookies
        driver.refresh()
        print("Logged in using saved cookies!")

        # Navigate through page to submit appeals form
        if not locate_and_click(driver, "tcp-nav-messages-hdr-responsive"):
            print("Failed during navigation. Exiting.")
            return False
        if not locate_and_click(driver, "btnComposeMessage"):
            print("Failed during navigation. Exiting.")
            return False
        locate_and_click(driver, "ddlNewMsgCat_button")
        locate_and_click(driver, "ddlNewMsgCat_option-14")
        locate_and_click(driver, "ddlNewMsgCatSub_button")
        locate_and_click(driver, "ddlNewMsgCatSub_option-0")
        locate_and_click(driver, "rbtnAppealType-appealGreivance-1")
        fill_input_field(driver, By.ID, "txtEmail-appealGreivance", "example@example.com")
        fill_input_field(driver, By.ID, "txtAddDetail-appealGreivance", 
                         "This is additional information about my grievance or appeal.")
        
        # Click the submit button
        locate_and_click(driver, "mcv2-griev-appeal-submit")
        locate_and_click(driver, "btnSubmitMsg")

        if intercepted_requests:
            print("Form submission was intercepted successfully.")
            return True
        
        print("No form submission request detected.")
        return False

    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
        return False

    finally:
        driver.execute_cdp_cmd("Fetch.disable", {})
        driver.quit()

def main():

    # Log in and save cookies to file
    driver = uc.Chrome()
    driver.get("https://membersecure.anthem.com/member/find-care")
    input("Log in manually and press Enter...")
    save_cookies(driver, "cookies.pkl")

    # Load cookies from file and add to driver
    load_cookies(driver, "cookies.pkl") 
    driver.refresh()

    print("Cookies loaded. Browser will remain open.")
    check_form_submission(driver)
    input("Press Enter to quit...")

if __name__ == "__main__":
    main()