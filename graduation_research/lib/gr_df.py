import pandas as pd
from django_pandas.io import read_frame
from review_based_recommender.models import Spot, Review, City
from graduation_research.lib import word_process


class ReviewData:
    def __init__(self, method_name='reviews2tokens_by_simple_parse'):
        self.df = self.create_df()
        print('created_dataframe')
        self.create_reviews_list()
        print('created_reviews_list_column')
        self.convert_tokens_df(method_name)

    @classmethod
    def create_df(cls):
        reviews = Review.objects.all()
        review_df = read_frame(reviews, fieldnames=['id', 'username', 'title', 'content', 'spot_id'], verbose=False)
        return review_df

    def create_reviews_list(self):
        self.df = self.df.groupby('spot_id').apply(ReviewData.get_reviews_list).to_frame('reviews').reset_index()

    @classmethod
    def get_reviews_list(cls, df):
        content_list = df.loc[:]['content'].tolist()
        title_list = df.loc[:]['title'].tolist()
        res = title_list + content_list
        return res

    def convert_tokens_df(self, method_name='reviews2tokens_by_simple_parse'):
        stopwords = word_process.get_stop_words()
        self.df['review_tokens'] = self.df['reviews'].apply(lambda doc: getattr(word_process, method_name)(doc, stopwords))
