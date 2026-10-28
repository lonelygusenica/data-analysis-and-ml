import numpy as np
from sklearn.tree import DecisionTreeRegressor

class MyBagging:

    def __init__(self, n_estimators=10, max_depth=None, random_state=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.models = []

    def fit(self, X, y):

        np.random.seed(self.random_state)

        N = X.shape[0]

        self.models = []

        for i in range(self.n_estimators):

            # bootstrap
            indices = np.random.choice(N, N, replace=True)

            X_sample = X[indices]
            y_sample = y[indices]

            # обучаем дерево
            tree = DecisionTreeRegressor(max_depth=self.max_depth)
            tree.fit(X_sample, y_sample)

            self.models.append(tree)

    def predict(self, X):

        predictions = []

        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)

        predictions = np.array(predictions)

        return predictions.mean(axis=0)