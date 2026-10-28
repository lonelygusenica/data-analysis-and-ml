import numpy as np

class MyPolynomialRegression:
    
    def __init__(self, degree=1, lr=0.01, n_iters=1000):
        self.degree = degree
        self.lr = lr
        self.n_iters = n_iters
        self.weights = None 
        self.bias = None     #свободный член 
        self.costs = None
        self.method = None

    # Создание полиномиальных признаков
    def _create_features(self, X):
        X = np.asarray(X)
        # Если X двумерный с одним признаком, преобразуем в одномерный
        if X.ndim == 2 and X.shape[1] == 1:
            X = X.flatten()
        n_samples = len(X)
        X_poly = np.ones((n_samples, self.degree + 1))  # матрица признаков с единицами
        for i in range(1, self.degree + 1):
            X_poly[:, i] = X ** i
        return X_poly  # возвращаем расширенную матрицу признаков

    # MSE
    def _compute_cost(self, X, y):
        n_samples = len(y)
        y_pred = X @ self.weights
        errors = y_pred - y
        return (1 / (2 * n_samples)) * np.sum(errors ** 2) #среднеквадратичная ошибка

    def fit(self, X, y, method="normal", tol=None):
        X_poly = self._create_features(X)
        y = np.asarray(y)
        self.method = method
        n_samples, n_features = X_poly.shape

        if method == "normal":
            # Нормальное уравнение
            self.weights = np.linalg.pinv(X_poly.T @ X_poly) @ X_poly.T @ y
            self.bias = self.weights[0]  # сохраняем bias для совместимости

        elif method == "gd":
            # Градиентный спуск
            self.weights = np.zeros(n_features)
            self.bias = 0
            self.costs = []

            for _ in range(self.n_iters):
                y_pred = X_poly @ self.weights
                errors = y_pred - y

                dw = (1 / n_samples) * (X_poly.T @ errors) #градиент
                self.weights -= self.lr * dw

                self.bias = self.weights[0]

                cost = self._compute_cost(X_poly, y)
                self.costs.append(cost)

                if tol is not None and cost < tol:
                    break

        else:
            raise ValueError("method must be 'normal' or 'gd'")
        
        return self


    def predict(self, X):
        X_poly = self._create_features(X)
        return X_poly @ self.weights