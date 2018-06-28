import pandas as pd
from django_pandas.io import read_frame
from review_based_recommender.models import Spot, Review, City
from graduation_research.lib import word_process


def create():
    reviews = Review.objects.all()
    review_df = read_frame(reviews, fieldnames=['id', 'username', 'title', 'content', 'spot_id'], verbose=False)
    return review_df


def create_reviews_list(review_df):
    df = review_df.groupby('spot_id').apply(__get_reviews_list).to_frame('reviews').reset_index()
    return df


def __get_reviews_list(df):
    content_list = df.loc[:]['content'].tolist()
    title_list = df.loc[:]['title'].tolist()
    res = title_list + content_list
    return res


def convert_tokens_df(df):
    df['review_tokens'] = df['reviews'].apply(lambda doc: word_process.reviews2tokens_by_simple_parse(doc, word_process.get_stop_words()))
