import csv
import time
from playwright.sync_api import sync_playwright

INPUT_FILE = "coursera_data.csv"
OUTPUT_FILE = "coursera_data.csv"
TEST_MODE = False
TEST_LIMIT = 10
START_ROW = 50    
END_ROW = 6000      
SLEEP_TIME = 0.5    
HEADLESS = True    

def fetch_course_data(url, page):
    page.goto(url)
    page.wait_for_timeout(2500) 

    # Количество студентов
    students = "None"
    try:
        students_elem = page.query_selector("div.css-1qi3xup span strong span")
        if students_elem:
            students = students_elem.inner_text().replace("\u00A0", "").replace(" ", "")
    except:
        pass

    # Тип сертификата
    certificate = "None"
    try:
        cert_elem = page.query_selector("div.css-drc7pp")
        if cert_elem:
            certificate_text = cert_elem.inner_text().strip()
            certificate = certificate_text
    except:
        pass

    # Стоимость курса
    cost = "None"
    try:
        page_text = page.content().lower()
        if "free" in page_text and "certificate" in page_text:
            cost = "Free + paid certificate"
        elif "free" in page_text:
            cost = "Free"
        elif "subscription" in page_text:
            cost = "Subscription"
        elif "one-time payment" in page_text or "purchase" in page_text:
            cost = "Fully paid"
        else:
            cost = "Paid / Subscription"
    except:
        pass

    # Рейтинг
    rating = "None"
    try:
        script_elem = page.query_selector("script[type='application/ld+json']")
        if script_elem:
            import json
            data = json.loads(script_elem.inner_text())
            rating_val = data.get("aggregateRating", {}).get("ratingValue")
            if rating_val:
                rating = str(rating_val)
    except:
        pass

    return students, certificate, cost, rating

def main():
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    total = len(rows)
    start_idx = START_ROW
    end_idx = END_ROW if END_ROW else total

    if TEST_MODE:
        print(f"TEST MODE: обрабатываются первые {TEST_LIMIT} строк\n")
        process_limit = min(TEST_LIMIT, total)
        start_idx = 0
        end_idx = process_limit
    else:
        print(f"FULL MODE: обрабатываются строки с {start_idx + 1} по {end_idx}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        for i in range(start_idx, end_idx):
            row = rows[i]
            url = row.get("url")
            if not url:
                print(f"[{i+1}/{end_idx}] {row.get('title')} → NO URL")
                continue

            print(f"[{i+1}/{end_idx}] {row.get('title')} → ", end="")
            students, certificate, cost, rating = fetch_course_data(url, page)
            updated = False

            if students != "None":
                row["learner_count"] = students
                updated = True
            if certificate != "None":
                row["certificate_type"] = certificate
                updated = True
            if cost != "None":
                row["cost"] = cost
                updated = True
            if rating != "None":
                row["rating"] = rating
                updated = True

            print("UPDATED" if updated else "NO DATA FOUND")
            time.sleep(SLEEP_TIME)

        browser.close()

    # Сохраняем обратно в CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n✅ coursera_data.csv успешно обновлён")

if __name__ == "__main__":
    main()
