import yaml
from graduation_research.lib.gr_df import ReviewData
from graduation_research.lib.gr_docs import GrDocs
from gensim import corpora, models, similarities
import os


class GraduationResearch:
    def __init__(self, method_name='default'):
        f = open("{}/settings.yml".format(os.path.dirname(os.path.abspath(__file__))), "r+")
        data = yaml.load(f)
        self.settings = data
        print(self.settings)
        self.method_name = method_name
        print(self.method_name)
        self.setting = data[method_name]
        self.df = self.make_df()
        dic_corpus = self.make_dic_corpus()
        self.dic = dic_corpus[0]
        self.corpus = dic_corpus[1]
        self.lda = self.get_lda()
        self.doc_index = similarities.docsim.MatrixSimilarity(self.lda[self.corpus])

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

    def save(self):
        self.dic.save_as_text("{}_dict.txt".format(self.method_name))
        corpora.MmCorpus.serialize("{}_cop.mm".format(self.method_name), self.corpus)
        self.lda.save("{}_lda.model".format(self.method_name))
        self.doc_index.save("{}_sim".format(self.method_name))
        self.df.to_pickle("{}_df".format(self.method_name))
