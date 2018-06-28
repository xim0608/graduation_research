from review_based_recommender.models import Spot
from gensim import similarities


class GrRecommend():
    def __init__(self, df, lda, corpus):
        self.lda = lda
        self.corpus = corpus
        self.doc_index = similarities.docsim.MatrixSimilarity(lda[corpus])
        # TODO: 処理ロジック別にpicklesにしておいたものを呼び出す
        self.df = df

    def get_recommends(self, base_doc_id):
        c = self.corpus[base_doc_id]
        vec_lda = self.lda[c]
        s = self.doc_index.__getitem__(vec_lda)
        s = sorted(enumerate(s), key=lambda t: t[1], reverse=True)
        spot_ids = []
        for doc_id, sim in s[1:10]:
            spot_ids.append(self.df.iloc[doc_id].spot_id)
        return Spot.objects.filter(id__in=spot_ids)
