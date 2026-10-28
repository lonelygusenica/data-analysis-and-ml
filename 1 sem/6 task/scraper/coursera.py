import requests
import json
import urllib.parse

from base import Course, Platform
from coursera_html import fetch_course_html_data


class Coursera(Platform):
    name = 'Coursera'

    def __init__(self):
        self.partner_ids = fetch_partners()

    def _urls(self):
        """
        Генерируем URL, пока API возвращает элементы
        """
        urls = []
        start = 0
        limit = 100

        while True:
            url = make_url(start=start, limit=limit)
            res = requests.get(url)
            data = json.loads(res.text)

            elements = data.get("elements", [])
            if not elements:
                break

            urls.append(url)
            start += limit

        return urls

    def _parse(self, url):
        courses = []
        res = requests.get(url)
        data = json.loads(res.text)

        for element in data.get("elements", []):
            if 'en' not in element.get('primaryLanguages', []):
                continue

            title = element.get('name')
            description = element.get('description', '')
            partners = [self.partner_ids.get(i) for i in element.get('partnerIds', [])]

            tags = []
            for d in element.get('domainTypes', []):
                tags.append(d['domainId'].replace('-', ' '))
                tags.append(d['subdomainId'].replace('-', ' '))

            course_url = 'https://www.coursera.org/learn/' + element['slug']

            html = fetch_course_html_data(course_url)

            course = Course(
                title=title,
                partners=partners,
                platform=self.name,
                description=description,
                tags=tags,
                url=course_url,
                rating=html.get("rating"),
                learner_count=html.get("learner_count"),
                certificate_type=html.get("certificate_type"),
                difficulty_workload=element.get("workload"),
                cost=html.get("cost")
            )

            courses.append(course)

        return courses


def make_url(start=0, limit=100):
    params = {
        'q': 'search',
        'start': start,
        'limit': limit,
        'fields': ','.join([
            'name',
            'description',
            'partnerIds',
            'slug',
            'primaryLanguages',
            'domainTypes',
            'workload'
        ])
    }
    return 'https://api.coursera.org/api/courses.v1?' + urllib.parse.urlencode(params)


def fetch_partners():
    res = requests.get('https://api.coursera.org/api/partners.v1')
    data = json.loads(res.text)
    return {el['id']: el['name'] for el in data.get('elements', [])}
