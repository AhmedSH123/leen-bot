# scraper/scrape_leen.py

import requests
from bs4 import BeautifulSoup
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

BASE_URL = "https://leen.sa"

def scrape_courses():
    url = f"{BASE_URL}/courses"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all course cards using the <h3> title anchor as entry point
    course_blocks = soup.find_all("h3", class_="text-black text-base break-words font-semibold group-hover:text-primary")

    courses = []

    for h3 in course_blocks:
        a_tag = h3.find("a")
        if not a_tag:
            continue
        title = a_tag.text.strip()
        relative_link = a_tag.get("href")
        full_link = BASE_URL + relative_link

        # Now go to the course detail page
        detail_resp = requests.get(full_link)
        detail_soup = BeautifulSoup(detail_resp.text, "html.parser")

        description_tag = detail_soup.find("div", class_="abjad-rich-text") or detail_soup.find("main")
        description = description_tag.get_text(separator="\n", strip=True) if description_tag else "No description found."

        # Extract optional fields like price and date
        price_tag = detail_soup.find("ins", class_="text-base font-bold no-underline text-success")
        price = price_tag.text.strip() if price_tag else "Not listed"

        start_date_tag = detail_soup.find("span", class_="text-black text-sm break-words font-medium !text-gray-700")
        start_date = start_date_tag.text.strip() if start_date_tag else "Not listed"

        courses.append({
            "title": title,
            "url": full_link,
            "description": description,
            "price": price,
            "start_date": start_date
        })

    os.makedirs("data", exist_ok=True)
    with open("data/courses.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print(f"✅ Scraped {len(courses)} courses.")





def scrape_faqs():
    options = Options()
    options.add_argument("--headless")  # Run without opening browser window
    driver = webdriver.Chrome(options=options)

    url = f"{BASE_URL}/faq"
    driver.get(url)

    time.sleep(3)  # Wait for content to load

    # Expand all collapsible FAQ blocks
    buttons = driver.find_elements(By.CLASS_NAME, "abjad-collapse-button")
    for btn in buttons:
        try:
            btn.click()
            time.sleep(0.3)
        except:
            pass  # Ignore errors for non-clickable

    # Grab all FAQ containers
    faq_containers = driver.find_elements(By.CLASS_NAME, "abjad-collapse")
    faqs = []

    for container in faq_containers:
        try:
            question_el = container.find_element(By.CLASS_NAME, "text-base")
            answer_el = container.find_element(By.CLASS_NAME, "abjad-collapse-content")
            faqs.append({
                "question": question_el.text.strip(),
                "answer": answer_el.text.strip()
            })
        except:
            continue

    driver.quit()

    os.makedirs("data", exist_ok=True)
    with open("data/faqs.json", "w", encoding="utf-8") as f:
        json.dump(faqs, f, indent=2, ensure_ascii=False)

    print(f"✅ Scraped {len(faqs)} FAQs.")



if __name__ == "__main__":
    scrape_courses()
    scrape_faqs()
