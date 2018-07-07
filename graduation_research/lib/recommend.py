from gensim import models, similarities, corpora
from review_based_recommender.models import Spot
import numpy as np
import pickle
import os
import yaml


class Recommend:
    def __init__(self, method_name='default'):
        base_dir = os.path.dirname(os.path.abspath(__file__)) + '/bin'
        self.corpus = corpora.MmCorpus("{}/{}_cop.mm".format(base_dir, method_name))
        self.lda = models.ldamodel.LdaModel.load("{}/{}_lda.model".format(base_dir, method_name))
        self.d = corpora.Dictionary.load_from_text("{}/{}_dict.txt".format(base_dir, method_name))
        self.doc_index = similarities.docsim.MatrixSimilarity.load("{}/{}_sim".format(base_dir, method_name))
        # self.df = pickle.load(open('{}_df'.format(method_name), 'rb'))
        self.df_list = pickle.load(open('{}/{}_df_list'.format(base_dir, method_name), 'rb'))
        self.matrix = np.load("{}/{}_matrix.npz".format(base_dir, method_name))['m']

    def similarity_vec(self, base_doc_id):
        c = self.corpus[base_doc_id]
        vec_lda = self.lda[c]
        vec = self.doc_index.__getitem__(vec_lda)
        return vec

    def make_matrix(self):
        matrix = []
        for doc_id, spot_id in enumerate(self.df_list):
            matrix.append(self.similarity_vec(doc_id))
        return np.matrix(matrix)

    def find(self, base_doc_id):
        s = self.similarity_vec(base_doc_id)
        s = sorted(enumerate(s), key=lambda t: t[1], reverse=True)
        spot_ids = []
        for doc_id, sim in s[1:10]:
            spot_ids.append(self.df_list[doc_id])
        return Spot.objects.filter(id__in=spot_ids)

    def show_base_and_recommend(self, base_doc_id):
        s = Spot.objects.get(id=base_doc_id)
        return s, self.find(base_doc_id)

    def show_topics(self, doc_id):
        topics = sorted(self.lda.get_document_topics(self.corpus[doc_id]), key=lambda t: t[1], reverse=True)
        for t in topics[:10]:
            print("{}: {}".format(t[0], t[1]))
        for t in topics[:10]:
            print("Topic # ", t[0])
            self.get_topic_words(t[0])
            print("\n")

    def get_topic_words(self, topic_id):
        for t in self.lda.get_topic_terms(topic_id):
            print("{}: {}".format(self.d[t[0]], t[1]))
