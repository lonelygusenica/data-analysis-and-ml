from multiprocessing import Pool


class Course:

    def __init__(self, title, partners, platform,
                 description, tags, url, snippet='',
                 # Новые поля для сбора данных
                 rating=None, learner_count=None,
                 certificate_type=None, difficulty_workload=None, cost=None):
        self.title = title
        self.partners = partners
        self.platform = platform
        self.description = description
        self.tags = tags
        self.url = url

        # Сохраняем дополнительные поля
        self.rating = rating
        self.learner_count = learner_count
        self.certificate_type = certificate_type
        self.difficulty_workload = difficulty_workload
        self.cost = cost

        if snippet:
            self.snippet = snippet
        else:
            self.snippet = description.split('.')[0] + '.'

    def _dict(self):
        return {'title': self.title,
                'partners': self.partners,
                'platform': self.platform,
                'snippet': self.snippet,
                'description': self.description,
                'tags': self.tags,
                'url': self.url,
                # Добавляем новые поля для вывода в CSV
                'rating': self.rating,
                'learner_count': self.learner_count,
                'certificate_type': self.certificate_type,
                'difficulty_workload': self.difficulty_workload,
                'cost': self.cost}


class Platform:
    name = ''

    def courses(self):
        pool = Pool(10)
        result_sets = pool.map(self._parse, self._urls())
        return flatten(result_sets)

    def _urls(self):
        raise NotImplementedError()

    def _parse(self, url):
        raise NotImplementedError()


def flatten(list):
    return [item for sublist in list for item in sublist]

