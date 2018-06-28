from gensim import corpora, models
import logging
import numpy as np

logging.basicConfig(format='%(message)s', level=logging.INFO)

class GrLda:
    def __init__(self, corpus, dic, num_topics=50, passes=10):
        self.corpus = corpus
        self.dic = dic
        self.num_topics = num_topics
        self.passes = passes
        self.lda = self.create()

    def create(self):
        lda = models.ldamodel.LdaModel(corpus=self.corpus, id2word=self.dic, num_topics=self.num_topics, passes=self.passes)
        return lda

    def check_perplexity(self, lda, test_corpus):
        n = sum(count for doc in test_corpus for id, count in doc)
        print("出現単語数N: ", n)
        perplexity = np.exp2(-self.lda.log_perplexity(test_corpus))
        # https://www.slideshare.net/hoxo_m/perplexity
        print("perplexity:", perplexity)

    def get_topic_words(self, topic_id):
        for t in self.lda.get_topic_terms(topic_id):
            print("{}: {}".format(self.dic[t[0]], t[1]))

    def show_topics_words(self, count=10):
        for t in range(count):
            print("Topic # ",t)
            self.get_topic_words(t)
            print("\n")
