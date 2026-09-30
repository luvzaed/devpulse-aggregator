import pytest
import sqlite3
import sys
import os

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from models import Article
from database import DatabaseConnection


@pytest.fixture
def test_db():
    """Provides a clean in-memory database connection for each test."""
    # Use :memory: so no physical file is written to disk
    db = DatabaseConnection(db_name=":memory:")
    # Override relative path logic if using raw in-memory
    db.db_name = ":memory:"
    with db:
        yield db


def test_save_article_success(test_db):
    article = Article("GitHub", "test-repo", "https://github.com/test", "alice", 100)
    test_db.save_article(article)

    cursor = test_db.conn.cursor()
    cursor.execute("SELECT source, title, url, author, score FROM trending_articles")
    rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0] == ("GitHub", "test-repo", "https://github.com/test", "alice", 100)


def test_duplicate_url_deduplication(test_db):
    article1 = Article("GitHub", "test-repo", "https://github.com/test", "alice", 100)
    # Identical URL, different score/title to test conflict resolution
    article2 = Article("GitHub", "test-repo-updated", "https://github.com/test", "alice", 150)

    test_db.save_article(article1)
    test_db.save_article(article2)

    cursor = test_db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trending_articles WHERE url = 'https://github.com/test'")
    count = cursor.fetchone()[0]

    # Verify UNIQUE(url) ignored the duplicate insert
    assert count == 1