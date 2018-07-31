from review_based_recommender.models import Spot


class MultiSpotsRecommend:
    def __init__(self, recommend):
        self.recommend = recommend

    def find_row(self, doc_id):
        return self.recommend.matrix[doc_id]

    def find(self, doc_ids=None, spot_ids=None):
        if doc_ids is None:
            doc_ids = list(map(self.recommend.convert_spot_id_to_doc_id, spot_ids))
        doc_ids = list(set(doc_ids))
        vec = self.find_row(doc_ids[0])
        for doc_id in doc_ids[1:]:
            vec += self.find_row(doc_id)
        s = sorted(enumerate(vec), key=lambda t: t[1], reverse=True)
        spot_ids = []
        recommend_limit_count = 10
        for doc_id, sim in s[1:10]:
            if doc_id not in doc_ids:
                spot_ids.append(self.recommend.df_list[doc_id])
                if len(spot_ids) >= recommend_limit_count:
                    break
        return Spot.objects.filter(id__in=spot_ids)

    def show_base_and_recommend(self, doc_ids):
        base_spot_ids = []
        for doc_id in doc_ids:
            base_spot_ids.append(self.recommend.df_list[doc_id])
        return Spot.objects.filter(id__in=base_spot_ids), self.find(doc_ids)
