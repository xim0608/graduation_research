import pandas as pd
from django_pandas.io import read_frame
from review_based_recommender.models import Spot, Review, City
from gensim import corpora, models


class GrDocs:
    def __init__(self, df):
        self.docs = []
        for index, row in df.iterrows():
            self.docs.append(row.review_tokens)

    def dictionary(self, no_below=5, no_above=0.2):
        # reference: https://qiita.com/youyouyou/items/b2fa94af74c583c9d841
        d = corpora.Dictionary(self.docs)
        # 使われている文書の数がno_belowより少ない単語を無視し、no_aboveの割合以上の文書に出てくる単語を無視している
        d.filter_extremes(no_below=no_below, no_above=no_above)
        d.compactify()
        return d

    def corpus(self, dic):
        corpus = [dic.doc2bow(w) for w in self.docs]
        # test_size = int(len(corpus) * test_ratio)
        # test_corpus = corpus[:test_size]
        # train_corpus = corpus[test_size:]
        # return test_corpus, train_corpus
        return corpus