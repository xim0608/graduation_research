import slackweb
import os
import inspect


def optimize_num_topics():
    # perplexityを最小化するnum_topicsを求める
    from graduation_research.lib.gr_lda import GrLda
    from graduation_research.lib.gr_docs import GrDocs
    from graduation_research.lib.gr_df import ReviewData
    perplexities = {}
    for topic_num in range(5, 51):
        df = ReviewData(method_name='review2tokens_by_lemma_of_nouns_without_area_fix_areas_only_japanese').df
        gr_docs = GrDocs(df)
        dic = gr_docs.dictionary(no_above=5, no_below=0.2)
        corpus = gr_docs.corpus(dic=dic)
        grlda = GrLda(corpus=corpus, dic=dic, num_topics=50, passes=10)
        perplexity = grlda.check_perplexity()
        perplexities[topic_num] = perplexity
        notify(perplexities)
    notify(perplexities)


def notify(result):
    slack = slackweb.Slack(url=os.environ.get('SLACK_WEBHOOK_URL'))
    slack.notify(text="<!channel>\nscript done: {}\nresult: {}".format(inspect.stack()[1][3], result))