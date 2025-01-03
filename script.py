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

def check_website_status(url):
    """Retrieves the status of a website given the url."""
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            print(f"{url} is up")
        else:
            print(f"{url} returned status code {response.status_code}.")

    except requests.exceptions.RequestException as e:
        print(f"Error: {url} seems to be down. Details: {e}")

def fill_input_field(driver, locator_type, locator_value, text):
    """Reusable function to locate an input field and send text."""
    input_field = driver.find_element(locator_type, locator_value)
    input_field.send_keys(text)

def click_element(driver, locator_type, locator_value):
    """Reusable function to locate and click an element."""
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

def check_form_submission():
    """Function to automate form submission and error detection."""

    try: 
        
        # initiate Chrome driver
        driver = webdriver.Chrome()

        # open and decode pickled cookies file
        with open("cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        # refresh page to apply cookies
        driver.refresh()

        print("Logged in using saved cookies!")


        # username = os.getenv("USERNAME")
        # password = os.getenv("PASSWORD")

        # open login page
        # driver.get("https://www.anthem.com/ca/login/")

        # complete manual login
        # time.sleep(20)

        # # send login credentials
        # fill_input_field(driver, By.ID, "txtUsername", username)
        # fill_input_field(driver, By.ID, "txtPassword", password)

        # # click login button
        # click_element(driver, By.ID, "btnLogin")

        # # wait for webpage to change
        # WebDriverWait(driver, 10).until(
        #     EC.url_changes("https://www.anthem.com/ca/login/")
        # )

        # # click messages button
        # click_element(driver, By.ID, "tcp-nav-messages-hdr-responsive")

        # # click compose message
        # click_element(driver, By.ID, "btnComposeMessage")

        # # interact with dropdown and button fields
        # click_element(driver, By.ID, "ddlNewMsgCat_legend")
        # click_element(driver, By.XPATH, "//span[@data-text='Grievances / Appeals']")

        # click_element(driver, By.ID, "ddlNewMsgCatSub_legend")
        # click_element(driver, By.ID, "rbtnAppealType-appealGreivancePreview-1")
        # click_element(driver, By.ID, "rbtnContactPref-appealGreivancePreview-0")

        # # fill out email and appeal details
        # fill_input_field(driver, By.ID, "txtEmail-appealGreivancePreview", "example@example.com")
        # click_element(driver, By.ID, "rbtnPatient-appealGreivancePreview-0")
        # fill_input_field(driver, By.ID, "txtAddDetail-appealGreivancePreview", 
        #                  "This is additional information about my grievance or appeal.")

        # # submit the form
        # click_element(driver, By.ID, "submit")
        # time.sleep(2)

        # try to find an error message upon submission
        try:
            error_message = driver.find_element(By.CLASS_NAME, "error-message").text
            print(f"Error detected: {error_message}")
            return False
        except NoSuchElementException:
            print("Form submitted successfully!")
            return True

    except TimeoutException as e:
        print(f"Timeout occurred: {e}")
        return False
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
    finally:
        driver.quit()


def main():

    # Log in and save cookies to file
    driver = uc.Chrome()
    driver.get("https://membersecure.anthem.com/member/find-care")
    input("Log in manually and press Enter...")
    save_cookies(driver, "cookies.pkl")

    # Load cookies from file and add to driver
    load_cookies(driver, "cookies.pkl")
    with open("cookies.pkl", "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            print(cookie)
        
    driver.refresh()

    print("Cookies loaded. Browser will remain open.")
    input("Press Enter to quit...")

if __name__ == "__main__":
    main()