import numpy as np
from collections import Counter

class MyKNN:
    def __init__(self, k=3):
        self.k = k
        self.X_train = None
        self.y_train = None

    def fit(self, X_train, y_train):
        self.X_train = np.array(X_train) 
        self.y_train = np.array(y_train) 

    # Вычисление евклидова расстояния между двумя точками
    def _euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2) ** 2))

    # Предсказание класса для одного объекта
    def predict_one(self, x):
        # Вычисляем расстояния от x до всех точек обучающей выборки
        distances = [self._euclidean_distance(x, xi) for xi in self.X_train]
        
        # Получаем индексы k ближайших соседей
        k_indices = np.argsort(distances)[:self.k]
        
        # Берем классы k ближайших соседей
        k_labels = self.y_train[k_indices]
        
        # Голосование: выбираем класс с наибольшим количеством голосов
        most_common = Counter(k_labels).most_common(1)
        return most_common[0][0]

    # Предсказание классов для набора объектов
    def predict(self, X_test):
        X_test = np.array(X_test)
        return np.array([self.predict_one(x) for x in X_test])

    # Вычисление точности классификатора на тестовой выборке
    def accuracy(self, X_test, y_test):
        y_pred = self.predict(X_test)
        return np.mean(y_pred == y_test) * 100