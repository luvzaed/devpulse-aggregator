class Article:
    def __init__(self, source: str, title: str, url: str, author: str, score: int):
        self.source = source
        self.title = title
        self.url = url
        self.author = author
        self.score = score

    def __repr__(self):
        return f"[{self.source}] {self.title} (Score: {self.score}) by @{self.author}"


class ArticleCollection:
    def __init__(self):
        self._articles = []

    def add(self, article: Article):
        self._articles.append(article)

    def __len__(self):
        return len(self._articles)

    def __iter__(self):
        return iter(self._articles)

    def __repr__(self):
        return f"<ArticleCollection: {len(self._articles)} articles>"