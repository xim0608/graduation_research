import yaml
from graduation_research.lib.gr_df import ReviewData
from graduation_research.lib.gr_docs import GrDocs
from gensim import corpora, models, similarities
import os
import pickle
import time
import numpy as np


class GraduationResearch:
    def __init__(self, method_name='default'):
        self.start_time = time.time()
        f = open("{}/settings.yml".format(os.path.dirname(os.path.abspath(__file__))), "r+")
        data = yaml.load(f)
        self.settings = data
        print(self.settings)
        self.method_name = method_name
        print(self.method_name)
        self.setting = data[method_name]
        self.df = self.make_df()
        self.df_list = self.df['spot_id'].tolist()
        dic_corpus = self.make_dic_corpus()
        self.dic = dic_corpus[0]
        self.corpus = dic_corpus[1]
        self.lda = self.get_lda()
        self.doc_index = similarities.docsim.MatrixSimilarity(self.lda[self.corpus])
        self.matrix = self.make_matrix()

    def make_df(self):
        # 前処理したdataframeを作成する
        df = ReviewData(method_name=self.setting['preprocess_method']).df
        return df

    def make_dic_corpus(self):
        gr_docs = GrDocs(self.df)
        dic = gr_docs.dictionary(no_above=self.setting['no_above'], no_below=self.setting['no_below'])
        corpus = gr_docs.corpus(dic=dic)
        return dic, corpus

    def get_lda(self):
        lda = models.ldamodel.LdaModel(corpus=self.corpus, id2word=self.dic,
                                       num_topics=self.setting['num_topics'], passes=self.setting['passes'])
        return lda

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

    def save(self):
        base_dir = os.path.dirname(os.path.abspath(__file__)) + '/bin'
        self.dic.save_as_text("{}/{}_dict.txt".format(base_dir, self.method_name))
        corpora.MmCorpus.serialize("{}/{}_cop.mm".format(base_dir, self.method_name), self.corpus)
        self.lda.save("{}/{}_lda.model".format(base_dir, self.method_name))
        self.doc_index.save("{}/{}_sim".format(base_dir, self.method_name))
        # self.df.to_pickle("{}/{}_df".format(base_dir, self.method_name))
        with open("{}/{}_df_list".format(base_dir, self.method_name), 'wb') as f:
            pickle.dump(self.df_list, f)
        np.savez_compressed("{}/{}_matrix.npz".format(base_dir, self.method_name), m=self.matrix)
        elapsed_time = time.time() - self.start_time
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
