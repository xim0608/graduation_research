import MeCab
from graduation_research.lib import word_preprocess
import urllib.request
import unicodedata
from graduation_research import settings

if settings.DEBUG:
    mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
else:
    mecab = MeCab.Tagger('-d /usr/lib/mecab/dic/mecab-ipadic-neologd')
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


def review2tokens_by_nouns_and_adjectives(reviews, stopwords):
    tokens = []
    for review in reviews:
        for chunk in mecab.parse(review).splitlines()[:-1]:
            (surface, feature) = chunk.split('\t')
            if surface in stopwords:
                continue
            if feature.startswith('形容詞') or feature.startswith('名詞'):
                tokens.append(surface)
    return tokens


def review2tokens_by_lemma(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞", "動詞", "形容詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == u"*":
                    lemma = node.surface
                if lemma not in stopwords:
                    tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_nouns(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == u"*":
                    lemma = node.surface
                if lemma not in stopwords:
                    tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_except_nouns(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["動詞", "形容詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == u"*":
                    lemma = node.surface
                if lemma not in stopwords:
                    tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_nouns_without_area(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == "*":
                    lemma = node.surface
                if lemma not in stopwords or \
                        ((node.feature.split(",")[1] != "固有名詞") or (node.feature.split(",")[2] != "地域")):
                    tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_nouns_without_proper_nouns(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == "*":
                    lemma = node.surface
                if lemma not in stopwords and node.feature.split(",")[1] != "固有名詞":
                    tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_nouns_without_area_fix_areas(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == "*":
                    lemma = node.surface
                if lemma not in stopwords \
                        and node.feature.split(",")[2] != "地域" and node.feature.split(",")[1] != "固有名詞":
                    tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_nouns_without_area_fix_areas_only_japanese(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == "*":
                    lemma = node.surface
                if lemma not in stopwords \
                        and node.feature.split(",")[2] != "地域" and node.feature.split(",")[1] != "固有名詞":
                    if is_japanese(lemma):
                        tokens.append(lemma)
            node = node.next
    return tokens


def review2tokens_by_lemma_of_nouns_and_adjectives_without_area_only_japanese(reviews, stopwords):
    tokens = []
    for review in reviews:
        node = mecab.parseToNode(review)
        while node:
            pos = node.feature.split(",")[0]
            if pos in ["名詞", "形容詞"]:
                lemma = node.feature.split(",")[6]
                if lemma == "*":
                    lemma = node.surface
                if lemma not in stopwords \
                        and node.feature.split(",")[2] != "地域" and node.feature.split(",")[1] != "固有名詞":
                    if is_japanese(lemma):
                        tokens.append(lemma)
            node = node.next
    return tokens


def is_japanese(string):
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name \
        or "HIRAGANA" in name \
        or "KATAKANA" in name:
            return True
    return False
