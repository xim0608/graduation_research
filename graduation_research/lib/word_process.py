import MeCab
from graduation_research.lib import word_preprocess
import urllib.request

mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
mecab.parse('')


def __get_sloth_lib_stop_words():
    slothlib_path = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
    slothlib_file = urllib.request.urlopen(slothlib_path)
    slothlib_stopwords = [line.decode("utf-8").strip() for line in slothlib_file if line.decode("utf-8").strip() != '']
    return slothlib_stopwords


def get_stop_words():
    stopwords = ['\n', '、', '「', '」']
    stopwords += __get_sloth_lib_stop_words()
    print('created stopwords_list')
    return stopwords


def reviews2tokens(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(word_preprocess.normalize_neologd(review))
        while node:
            word = node.surface
            if word in stopwords:
                continue
            pos = node.feature.split(",")[1]
            node = node.next
            tokens.append(word)
    return tokens


def reviews2tokens_by_simple_parse(reviews, stopwords):
    tokens = []
    for review in reviews:
        for chunk in mecab.parse(review).splitlines()[:-1]:
            (surface, feature) = chunk.split('\t')
            if surface in stopwords:
                continue
            if feature.startswith('名詞'):
                # print(feature)
                tokens.append(surface)
    return tokens


def review2tokens_by_adjective(reviews, stopwords):
    tokens = []
    for review in reviews:
        for chunk in mecab.parse(review).splitlines()[:-1]:
            (surface, feature) = chunk.split('\t')
            if surface in stopwords:
                continue
            if feature.startswith('形容詞'):
                # print(feature)
                tokens.append(surface)
    return tokens
