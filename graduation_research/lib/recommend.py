from gensim import models, similarities, corpora
from review_based_recommender.models import Spot
import pickle


class Recommend:
    def __init__(self, method_name='default'):
        self.corpus = corpora.MmCorpus("{}_cop.mm".format(method_name))
        self.lda = models.ldamodel.LdaModel.load("{}_lda.model".format(method_name))
        self.d = corpora.Dictionary.load_from_text("{}_dict.txt".format(method_name))
        self.doc_index = similarities.docsim.MatrixSimilarity.load("{}_sim".format(method_name))
        # self.df = pickle.load(open('{}_df'.format(method_name), 'rb'))
        self.df_list = pickle.load(open('{}_df_list'.format(method_name), 'rb'))

    def find(self, base_doc_id):
        c = self.corpus[base_doc_id]
        vec_lda = self.lda[c]
        s = self.doc_index.__getitem__(vec_lda)
        s = sorted(enumerate(s), key=lambda t: t[1], reverse=True)
        spot_ids = []
        for doc_id, sim in s[1:10]:
            spot_ids.append(self.df_list[doc_id])
        return Spot.objects.filter(id__in=spot_ids)
