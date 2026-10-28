import numpy as np
from sklearn.tree import DecisionTreeRegressor

class MyRandomForestRegressor:

    def __init__(self, n_trees=20, max_depth=3, bootstrap_size=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.bootstrap_size = bootstrap_size
        self.trees = []

    def bootstrap_sample(self, data):
        if self.bootstrap_size is None:
            self.bootstrap_size = len(data)
        indices = np.random.randint(0, len(data), self.bootstrap_size)
        return data.iloc[indices]

    def _buildDecisionTree(self, df):
        tree = DecisionTreeRegressor(max_depth=self.max_depth)
        tree.fit(df[df.columns[:-1]], df[df.columns[-1]])  # последний столбец — y
        return tree

    def _decisionTreePredictions(self, df, tree):
        return tree.predict(df[df.columns[:-1]])

    def fit(self, data):
        self.trees = []
        for i in range(self.n_trees):
            sample = self.bootstrap_sample(data)
            tree = self._buildDecisionTree(sample)
            self.trees.append(tree)

    def predict(self, data):
        predictions = np.array([self._decisionTreePredictions(data, tree) for tree in self.trees])
        return predictions.mean(axis=0)