import numpy as np

class MultipleInstanceRecommend:
    def __init__(self, recommend_instances, weights):
        if len(recommend_instances) != len(weights):
            raise InconsistentListLengthException
        self.recommend_instances = recommend_instances
        self.matrices = self.make_matrix()
        self.weights = weights

    def make_matrix(self):
        matrices = []
        for recommend_instance in self.recommend_instances:
            matrices.append(recommend_instance.matrix)
        return matrices

    def calculate(self):
        M = np.matrix(self.matrices[0])
        for matrix in self.matrices[1:]:
            M += matrix
        return M


class InconsistentListLengthException(Exception):
    def __str__(self):
        return 'Setting List Length does not match Recommend instances'
