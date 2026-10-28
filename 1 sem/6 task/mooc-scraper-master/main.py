# В отдельном тестовом файле
import requests
import json
# Импортируйте make_url из вашего coursera.py, если это возможно,
# или скопируйте ее сюда.

# ... (скопируйте make_url сюда с измененным кодом выше) ...

test_url = make_url()
res = requests.get(test_url)

# Вывод полного JSON-ответа для анализа
print(json.dumps(json.loads(res.text), indent=4))