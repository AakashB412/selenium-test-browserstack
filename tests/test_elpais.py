import re
import time
import requests

from pathlib import Path
from collections import Counter

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager

from deep_translator import GoogleTranslator

# ==================================================
# Configuration
# ==================================================

BASE_URL = "https://elpais.com"
OPINION_URL = "https://elpais.com/opinion/"

IMAGE_DIR = Path("article_images")
IMAGE_DIR.mkdir(
    exist_ok=True
)

# ==================================================
# Browser
# ==================================================

def create_driver():

    options = Options()

    options.add_argument(
        "--start-maximized"
    )
    options.add_argument(
        "--disable-notifications"
    )

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    return driver

# ==================================================
# Page helpers
# ==================================================

def wait_for_page(driver):

    WebDriverWait(
        driver,
        30
    ).until(
        lambda d:
        d.execute_script(
            "return document.readyState"
        )
        ==
        "complete"
    )

def accept_cookies(driver):
    """
    Handles the cookie consent banner.
    """

    possible_buttons = [
        "Accept",
        "Accept all",
        "ACCEPT AND CONTINUE"
    ]

    for text in possible_buttons:

        try:
            button = WebDriverWait(
                driver,
                5
            ).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{text.lower()}')]"
                    )
                )
            )

            button.click()

            print(
                "Cookie banner accepted"
            )
            time.sleep(2)
            return True

        except Exception:
            pass

    return False

def handle_authentication_slider(driver):
    """
    Waits only if the authentication slider is visible.
    """

    try:
        slider = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.sliderText")
            )
        )

        if "Slide right to secure your access" in slider.text:
            print("Authentication slider detected.")
            print("Please complete it manually...")

            WebDriverWait(driver, 300).until_not(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.sliderText")
                )
            )

            print("Authentication completed.")

    except TimeoutException:
        # No slider present
        pass

def check_language(driver):

    lang = driver.execute_script(
        "return document.documentElement.lang"
    )

    print(
        "Detected language:",
        lang
    )

# ==================================================
# Get opinion articles
# ==================================================

def get_opinion_articles(driver):

    driver.get(
        OPINION_URL
    )

    wait_for_page(driver)

    accept_cookies(driver)

    wait_for_page(driver)

    handle_authentication_slider(driver)

    articles = []

    seen = set()

    article_cards = driver.find_elements(
    By.TAG_NAME,
    "article"
    )

    for card in article_cards:

        try:
            headline = card.find_element(
            By.CSS_SELECTOR,
            "h2 a"
            )
        except NoSuchElementException:
            continue

        title = headline.text.strip()
        url = headline.get_attribute("href")

        if (
        title
        and url
        and url not in seen
        ):
            articles.append(
                {
                "title": title,
                "url": url
                }
            )

            seen.add(url)

        if len(articles) == 5:
            break

    return articles

# ==================================================
# Scrape article
# ==================================================

def scrape_article(driver, article):

    driver.get(
        article["url"]
    )

    if "/opinion/" not in driver.current_url:
        return None

    wait_for_page(driver)

    accept_cookies(driver)

    handle_authentication_slider(driver)

    title = driver.find_element(
        By.TAG_NAME,
        "h1"
    ).text

    article_body = driver.find_element(
    By.TAG_NAME,
    "article"
    )

    paragraphs = article_body.find_elements(
    By.TAG_NAME,
    "p"
    )

    content = "\n".join(
        [
            p.text.strip()
            for p in paragraphs
            if p.text.strip()
        ]
    )

    image = download_image(
        driver,
        title
    )

    return {

        "title": title,

        "content": content,

        "image": image
    }

# ==================================================
# Download cover image
# ==================================================

def download_image(driver,title):

    try:

        img = driver.find_element(
            By.CSS_SELECTOR,
            "figure img"
        )

        url = img.get_attribute(
            "src"
        )

        if not url:
            return None

        filename = re.sub(
            r"[^a-zA-Z0-9]",
            "_",
            title[:40]
        )

        path = (
            IMAGE_DIR /
            f"{filename}.jpg"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        path.write_bytes(
            response.content
        )

        return str(path)

    except Exception:

        return None

# ==================================================
# Language Translation
# ==================================================

def translate_titles(titles):

    translated = []

    translator = GoogleTranslator(
        source="auto",
        target="en"
    )

    for title in titles:
        translated.append(
            translator.translate(title)
        )

    return translated

# ==================================================
# Analyze headers
# ==================================================

def find_repeated_words(headers):

    words = []

    for header in headers:

        tokens = re.findall(

            r"\b[a-zA-Z]+\b",

            header.lower()

        )

        words.extend(tokens)

    counts = Counter(words)

    return {

        word: count

        for word,count

        in counts.items()

        if count > 2

    }

# ==================================================
# Main
# ==================================================

def main():

    driver = create_driver()

    try:

        driver.get(
            BASE_URL
        )

        wait_for_page(driver)

        accept_cookies(driver)

        handle_authentication_slider(driver)

        check_language(driver)

        print(
            "\nGetting Opinion articles..."
        )

        articles = get_opinion_articles(
            driver
        )

        scraped_articles = []

        for article in articles:

            print(
                "\nOpening:",
                article["url"]
            )

            data = scrape_article(
                driver,
                article
            )

            if data is None:
                 continue

            scraped_articles.append(data)

            print(
                "\nTITLE:"
            )

            print(
                data["title"]
            )

            print(
                "\nCONTENT:"
            )

            print(
                data["content"][:500]
            )

            print(
                "\nIMAGE:",
                data["image"]
            )

        titles = [

            article["title"]

            for article

            in scraped_articles

        ]

        translated_headers = translate_titles(
            titles
        )

        print(
            "\n\nTranslated Headers:"
        )


        for header in translated_headers:

            print(
                "-",
                header
            )

        repeated = find_repeated_words(
            translated_headers
        )


        print(
            "\nRepeated words:"
        )


        for word,count in repeated.items():

            print(
                f"{word}: {count}"
            )

    finally:

        driver.quit()

if __name__ == "__main__":

    main()