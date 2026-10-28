import numpy as np
import random

class KMeans:

    def __init__(self, n_clusters=3, max_iter=10):
        self.n_clusters = n_clusters  # количество кластеров
        self.max_iter = max_iter  # максимальное количество итераций
        self.history = []   # сохраняем центроиды на каждой итерации для анализа

    def euclidean(self, point, data):
        # считаем евклидово расстояние от точки до всех точек в массиве
        return np.sqrt(np.sum((point - data)**2, axis=1))

    def fit(self, X):
        # случайно выбираем начальные центроиды
        self.centroids = X[np.random.choice(len(X), self.n_clusters, replace=False)]

        for _ in range(self.max_iter):
            clusters = [[] for _ in range(self.n_clusters)]  # создаём пустые списки для кластеров

            # распределяем точки по ближайшему центроиду
            for x in X:
                dists = self.euclidean(x, self.centroids)  # расстояние до всех центроидов
                idx = np.argmin(dists)  # индекс ближайшего центроида
                clusters[idx].append(x)  # добавляем точку в соответствующий кластер

            self.history.append(self.centroids.copy())  # сохраняем центроиды текущей итерации

            new_centroids = []

            # пересчитываем центроиды
            for i in range(self.n_clusters):
                if len(clusters[i]) == 0:  # если кластер пустой
                    new_centroids.append(self.centroids[i])  # оставляем старый центроид
                else:
                    new_centroids.append(np.mean(clusters[i], axis=0))  # среднее точек кластера

            new_centroids = np.array(new_centroids)

            # проверяем сходимость
            if np.allclose(self.centroids, new_centroids):
                break  # центроиды не изменились, алгоритм завершён

            self.centroids = new_centroids  # обновляем центроиды для следующей итерации

    def predict(self, X):
        labels = []
        # присваиваем каждой точке ближайший кластер
        for x in X:
            dists = self.euclidean(x, self.centroids)
            labels.append(np.argmin(dists))
        return labels