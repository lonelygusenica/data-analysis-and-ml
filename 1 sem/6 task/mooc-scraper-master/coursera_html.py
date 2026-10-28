import requests
import json
import time
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# -----------------------------
# Простейший in-memory cache
# -----------------------------
HTML_CACHE = {}


def fetch_course_html_data(course_url: str,
                           retries: int = 3,
                           sleep_time: float = 0.5) -> dict:
    """
    HTML-допарсинг страницы Coursera.
    Возвращает:
    rating, learner_count, certificate_type, cost
    """

    if course_url in HTML_CACHE:
        return HTML_CACHE[course_url]

    result = {
        "rating": None,
        "learner_count": None,
        "certificate_type": None,
        "cost": None
    }

    for attempt in range(retries):
        try:
            response = requests.get(
                course_url,
                headers=HEADERS,
                timeout=15
            )
            response.raise_for_status()
            break
        except Exception:
            if attempt == retries - 1:
                HTML_CACHE[course_url] = result
                return result
            time.sleep(2)
    else:
        HTML_CACHE[course_url] = result
        return result

    soup = BeautifulSoup(response.text, "html.parser")

    # ------------------------------------------------
    # 1. JSON-LD (rating)
    # ------------------------------------------------
    json_ld = soup.find("script", type="application/ld+json")
    if json_ld:
        try:
            data = json.loads(json_ld.string)
            aggregate = data.get("aggregateRating", {})
            result["rating"] = aggregate.get("ratingValue")
        except Exception:
            pass

    # ------------------------------------------------
    # 2. Количество студентов (ТОЧНОЕ)
    # Пример: "2 532 уже зарегистрированы"
    # ------------------------------------------------
    text = soup.get_text(separator=" ")
    match = re.search(r'([\d\s]+)\s+уже зарегистрированы', text)
    if match:
        count = match.group(1).replace(" ", "")
        try:
            result["learner_count"] = int(count)
        except ValueError:
            result["learner_count"] = None

    # ------------------------------------------------
    # 3. Тип сертификата
    # ------------------------------------------------
    if soup.find(string=re.compile("Certificate", re.IGNORECASE)):
        result["certificate_type"] = "Certificate available"
    else:
        result["certificate_type"] = None

    # ------------------------------------------------
    # 4. Тип стоимости (без цены)
    # ------------------------------------------------
    lower_text = text.lower()
    if "free" in lower_text and "certificate" in lower_text:
        result["cost"] = "Free + paid certificate"
    elif "subscription" in lower_text:
        result["cost"] = "Subscription"
    elif "free" in lower_text:
        result["cost"] = "Free"
    else:
        result["cost"] = "Paid"

    time.sleep(sleep_time)

    HTML_CACHE[course_url] = result
    return result
