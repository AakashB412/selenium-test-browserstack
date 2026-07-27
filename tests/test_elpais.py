from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def accept_cookies(wait):
    try:
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        cookie_button.click()
        print("Cookie banner accepted.")
    except Exception:
        print("Cookie banner not displayed.")


def test_open_elpais():

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()

    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://elpais.com")
        print("✓ Homepage opened")

        wait.until(EC.title_contains("EL PAÍS"))
        print("✓ Homepage loaded")

        time.sleep(2)

        print("Accepting cookies...")
        accept_cookies(wait)

        print("Looking for Opinion link...")
        opinion_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Opinión"))
        )
        print("✓ Opinion link found")

        print("Clicking Opinion...")
        opinion_link.click()

        print("Waiting for Opinion page...")
        wait.until(EC.url_contains("/opinion"))

        print("✓ Reached Opinion page")
        print("Current URL:", driver.current_url)
        print("Current Title:", driver.title)

        time.sleep(5)

        assert "/opinion" in driver.current_url

    finally:
        driver.quit()
