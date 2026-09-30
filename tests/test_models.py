import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from models import Article, ArticleCollection


def test_cross_source_normalization_and_ranking():
    collection = ArticleCollection()
    # GitHub has huge numbers, Dev.to has small numbers
    collection.add(Article("GitHub", "big-repo", "https://gh.com/1", "user1", 500000))
    collection.add(Article("GitHub", "mid-repo", "https://gh.com/2", "user2", 250000))
    collection.add(Article("Dev.to", "top-post", "https://dev.to/1", "user3", 50))
    collection.add(Article("Dev.to", "mid-post", "https://dev.to/2", "user4", 10))

    ranked = collection.get_ranked(top_n=3)

    # Limited to 3 items due to top_n=3
    assert len(ranked) == 3

    # Both #1 items from each source should have a normalized score of 100.0
    assert ranked[0].normalized_score == 100.0
    assert ranked[1].normalized_score == 100.0

    # The 50% GitHub repo (Norm: 50.0) should beat the 20% Dev.to post (Norm: 20.0)
    assert ranked[2].title == "mid-repo"
    assert ranked[2].normalized_score == 50.0