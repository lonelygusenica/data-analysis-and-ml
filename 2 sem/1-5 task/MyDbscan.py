import numpy as np

class MyDBSCAN:

    def __init__(self, eps=0.5, min_samples=5):
        self.eps = eps  # радиус окрестности для точки
        self.min_samples = min_samples  # минимальное количество точек для формирования кластера

    def euclidean(self, a, b):
        # считаем евклидово расстояние между двумя точками
        return np.sqrt(np.sum((a - b) ** 2))

    def region_query(self, X, point_idx):
        # ищем все точки, которые находятся в eps-окрестности от point_idx
        neighbors = []
        for i in range(len(X)):
            if self.euclidean(X[point_idx], X[i]) <= self.eps:
                neighbors.append(i)
        return neighbors

    def fit(self, X):
        # инициализация меток всех точек None
        self.labels = [None] * len(X)
        cluster_id = 0  # текущий id кластера

        for i in range(len(X)):

            if self.labels[i] is not None:
                continue  # точка уже обработана

            neighbors = self.region_query(X, i)  # ищем соседей

            if len(neighbors) < self.min_samples:
                self.labels[i] = -1  # помечаем как шум
                continue

            # создаём новый кластер
            cluster_id += 1
            self.labels[i] = cluster_id

            seeds = neighbors  # начинаем расширять кластер
            j = 0
            while j < len(seeds):

                point = seeds[j]

                if self.labels[point] == -1:
                    self.labels[point] = cluster_id  # шум становится частью кластера

                if self.labels[point] is not None:
                    j += 1
                    continue  # уже обработана, переходим к следующей

                self.labels[point] = cluster_id  # присваиваем кластер

                new_neighbors = self.region_query(X, point)  # ищем соседей этой точки

                if len(new_neighbors) >= self.min_samples:
                    seeds += new_neighbors  # расширяем кластер новыми точками

                j += 1

        return np.array(self.labels)  # возвращаем метки для всех точек