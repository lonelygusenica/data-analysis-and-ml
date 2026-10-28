import requests
import json
import urllib.parse


def make_test_url():
    """
    Создает URL для запроса API первой страницы каталога с лимитом 10 курсов.
    """

    params = {
        'start': 0,
        'limit': 10,  # Запрашиваем 10 курсов
        'fields': ','.join([
            # Базовые поля
            'name', 'description', 'partnerIds',
            'slug', 'primaryLanguages', 'domainTypes',
            # Поля для статистики, которые мы пытаемся найти
            'rating', 'learnerCount', 'courseType',
            'workload', 'primaryLanguageId', 's12nIds',
            'enrollmentCount', 'averageRating', 'stats',  # Добавляем stats для полноты
        ]),
        'includes': ','.join([
            'courseType', 'onDemandWorkload',
            'ratings', 'enrolledCount', 'stats'
        ])  # Добавляем includes для вложенных данных
    }
    # Используем основной URL каталога
    return 'https://api.coursera.org/api/courses.v1?' + urllib.parse.urlencode(params)


def test_api():
    test_url = make_test_url()

    print(f"Тестовый URL: {test_url}")

    # Выполняем запрос
    res = requests.get(test_url)

    try:
        # Пытаемся распарсить JSON
        data = json.loads(res.text)

        print("\n--- ПОЛНЫЙ JSON-ОТВЕТ API (для 10 курсов) ---")

        # Выводим весь JSON в читаемом формате (с отступами)
        print(json.dumps(data, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Ошибка при парсинге JSON: {e}")
        print(f"Статус-код ответа: {res.status_code}")
        print(f"Текст ответа (первые 500 символов): {res.text[:500]}...")


if __name__ == '__main__':
    test_api()