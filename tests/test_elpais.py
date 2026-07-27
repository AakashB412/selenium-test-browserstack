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

    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://elpais.com")

        wait.until(EC.title_contains("EL PAÍS"))

        time.sleep(2)

        accept_cookies(wait)

        # Find the Opinión link
        opinion_link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Opinión"))
        )

        # Click it
        opinion_link.click()

        # Wait for the Opinion page to load
        wait.until(EC.url_contains("/opinion"))

        print(driver.current_url)
        print(driver.title)

        assert "/opinion" in driver.current_url

        time.sleep(2)

        print(driver.title)

        assert "EL PAÍS" in driver.title

    finally:
        driver.quit()