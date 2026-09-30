import sqlite3
from models import Article
from config import DB_PATH


class DatabaseConnection:
    """A context manager for SQLite database connections."""
    def __init__(self, db_name: str = str(DB_PATH)):
        self.db_name = str(db_name)
        self.conn = None

    def __enter__(self):
        print(f"\n[Database] Connecting to {self.db_name}...")
        self.conn = sqlite3.connect(self.db_name)
        self._create_table()
        return self

    def __exit__(self, exc_type, exc_val, exc_traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
                print("[Database] Transaction committed and connection closed.")
            else:
                self.conn.rollback()
                print("[Database] Error detected. Transaction rolled back.")
            self.conn.close()
        return False

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS trending_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            url TEXT,
            author TEXT,
            score INTEGER,
            UNIQUE(url)
        )
        """
        self.conn.execute(query)

    def save_article(self, article: Article):
        query = """
        INSERT OR IGNORE INTO trending_articles (source, title, url, author, score)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(query, (article.source, article.title, article.url, article.author, article.score))


def stream_db_data(db_name: str = str(DB_PATH)):
    """A generator that reads from SQLite and yields one Article object at a time."""
    db_path = str(db_name)
    print(f"\n[Generator] Streaming articles from {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT source, title, url, author, score FROM trending_articles")
    
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        source, title, url, author, score = row
        yield Article(source=source, title=title, url=url, author=author, score=score)
        
    conn.close()