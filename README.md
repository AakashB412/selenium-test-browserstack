# EL PAÍS Web Scraper-BrowserStack Assignment

A Python automation project that uses Selenium WebDriver to scrape the latest opinion articles from the EL PAÍS website, download article cover images, translate article titles into English, and analyze the translated headers for repeated words.

---

## Features

* Opens the EL PAÍS website using Selenium WebDriver.
* Navigates to the **Opinion** section.
* Automatically accepts the cookie consent banner (when present).
* Scrapes the first **five** opinion articles.
* Extracts:
  * Article title
  * Article content
  * Cover image
* Downloads each article's cover image locally.
* Translates Spanish article titles into English using **deep-translator**.
* Identifies words that appear more than twice across the translated titles.

---

## Technologies Used

* Python 3
* Selenium
* Chrome WebDriver
* webdriver-manager
* requests
* deep-translator

---

## How to run

Execute the Python script in the tests folder:

python test_elpais.py -s

The script will:

1. Launch Chrome.
2. Open EL PAÍS.
3. Navigate to the Opinion section.
4. Scrape the first five opinion articles.
5. Download each article's cover image.
6. Translate article titles into English.
7. Display repeated words found in the translated titles.

Downloaded images will be saved inside the article_images folder.

---

## How to run on BrowserStack Automate

Execute the Python script in the tests folder:

browserstack-sdk python test_elpais.py -s

---

## Sample Output

```text
Detected language: es

Getting Opinion articles...

Opening:
https://elpais.com/opinion/...

TITLE:
...

CONTENT:
...

IMAGE:
article_images/example.jpg

Translated Headers:
- ...
- ...
- ...

Repeated words:
government: 3
europe: 4
```