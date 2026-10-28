import numpy as np

class MyDecisionTree:

    def __init__(self, max_depth=5, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None

    def _entropy(self, y):
        classes, counts = np.unique(y, return_counts=True)
        probs = counts / len(y)
        return -np.sum(probs * np.log2(probs))

    def _best_split(self, X, y):
        best_entropy = float("inf")  # инициализация минимальной энтропии
        best_feature = None  # лучший признак для разбиения
        best_threshold = None  # лучший порог для разбиения

        n_features = X.shape[1]  # количество признаков

        for feature in range(n_features): # перебираем возможные пороги

            values = np.unique(X[:, feature])

            for i in range(1, len(values)):
                threshold = (values[i] + values[i-1]) / 2

                left_mask = X[:, feature] <= threshold
                right_mask = X[:, feature] > threshold

                if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:  # если ветка пуста
                    continue

                y_left = y[left_mask]  # классы в левой ветке
                y_right = y[right_mask]  # классы в правой ветке

                p_left = len(y_left) / len(y)  # доля объектов в левой ветке
                p_right = len(y_right) / len(y)  # доля объектов в правой ветке

                entropy = p_left * self._entropy(y_left) + p_right * self._entropy(y_right)

                if entropy < best_entropy:
                    best_entropy = entropy
                    best_feature = feature
                    best_threshold = threshold

        return best_feature, best_threshold

    def _most_common(self, y):
        values, counts = np.unique(y, return_counts=True)
        return values[np.argmax(counts)]

    def _build_tree(self, X, y, depth):
        # проверка условий остановки
        if (len(np.unique(y)) == 1 or
            len(y) < self.min_samples_split or
            depth >= self.max_depth):

            return self._most_common(y) # возвращаем класс для листа

        feature, threshold = self._best_split(X, y)

        if feature is None:
            return self._most_common(y)

        left_mask = X[:, feature] <= threshold
        right_mask = X[:, feature] > threshold

        left_tree = self._build_tree(X[left_mask], y[left_mask], depth+1)
        right_tree = self._build_tree(X[right_mask], y[right_mask], depth+1)

        # возвращаем словарь узла с информацией о разбиении
        return {
            "feature": feature,
            "threshold": threshold,
            "left": left_tree,
            "right": right_tree
        }

    def fit(self, X, y):
        self.tree = self._build_tree(X, y, 0)  # строим дерево начиная с глубины 0

    def _predict_one(self, x, node):

        if not isinstance(node, dict): # если узел - лист
            return node # возвращаем класс

        if x[node["feature"]] <= node["threshold"]:# проверяем условие разбиения
            return self._predict_one(x, node["left"]) # идём в левую ветку
        else:
            return self._predict_one(x, node["right"])# идём в правую ветку

    def predict(self, X):
        return np.array([self._predict_one(x, self.tree) for x in X])