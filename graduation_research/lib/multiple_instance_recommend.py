import numpy as np
from review_based_recommender.models import Spot


class MultipleInstanceRecommend:
    def __init__(self, recommend_instances, weights):
        if len(recommend_instances) != len(weights):
            raise InconsistentListLengthException
        self.recommend_instances = recommend_instances
        self.weights = weights
        self.df_list = recommend_instances[0].df_list
        self.matrix = self.calc()

    def calc(self):
        m = self.recommend_instances[0].matrix * self.weights[0]
        for (recommend_instance, weight) in zip(self.recommend_instances[1:], self.weights[1:]):
            m += recommend_instance.matrix * weight
        return m

    def find(self, base_doc_id):
        s = self.matrix[base_doc_id]
        s = sorted(enumerate(s), key=lambda t: t[1], reverse=True)
        spot_ids = []
        for doc_id, sim in s[1:10]:
            spot_ids.append(self.recommend_instances[0].df_list[doc_id])
        return Spot.objects.filter(id__in=spot_ids)

    def show_base_and_recommend(self, base_doc_id):
        s = Spot.objects.get(id=base_doc_id)
        return s, self.find(base_doc_id)


class InconsistentListLengthException(Exception):
    def __str__(self):
        return 'Setting List Length does not match Recommend instances'
