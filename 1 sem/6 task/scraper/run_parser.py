import csv
import os
from coursera import Coursera


def main():
    parser = Coursera()
    courses = parser.courses()

    filename = 'coursera_data.csv'
    fieldnames = [
        'title', 'partners', 'platform', 'url',
        'rating', 'learner_count',
        'certificate_type', 'difficulty_workload',
        'cost', 'tags', 'snippet', 'description'
    ]

    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        if not file_exists:
            writer.writeheader()
        for c in courses:
            writer.writerow(c._dict())

    print(f'Сохранено курсов: {len(courses)}')


if __name__ == '__main__':
    main()
