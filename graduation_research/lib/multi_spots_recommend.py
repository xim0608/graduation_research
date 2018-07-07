from review_based_recommender.models import Spot


class MultiSpotRecommend:
    def __init__(self, recommend):
        self.recommend = recommend

    def find_rows(self, doc_id):
        return self.recommend.matrix[doc_id]

    def find(self, doc_ids):
        vec = self.find_rows(doc_ids[0])
        for doc_id in doc_ids[1:]:
            vec += self.find_rows(doc_id)
        s = sorted(enumerate(vec), key=lambda t: t[1], reverse=True)
        spot_ids = []
        for doc_id, sim in s[1:10]:
            spot_ids.append(self.df_list[doc_id])
        return Spot.objects.filter(id__in=spot_ids)
