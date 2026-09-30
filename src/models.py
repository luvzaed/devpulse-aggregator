class Article:
    def __init__(
        self,
        source: str,
        title: str,
        url: str,
        author: str,
        score: int,
        snippet: str = "",
        normalized_score: float = 0.0,
    ):
        self.source = source
        self.title = title
        self.url = url
        self.author = author
        self.score = score
        self.snippet = snippet or "No description available."
        self.normalized_score = normalized_score

    def __repr__(self):
        return (
            f"[{self.source}] {self.title} "
            f"(Score: {self.score} | Norm: {self.normalized_score:.1f}) by @{self.author}"
        )


class ArticleCollection:
    def __init__(self):
        self._articles: list[Article] = []

    def add(self, article: Article):
        self._articles.append(article)

    def get_ranked(self, top_n: int | None = None) -> list[Article]:
        """Normalizes scores per source on a 0-100 scale and returns sorted articles."""
        if not self._articles:
            return []

        max_scores: dict[str, int] = {}
        for article in self._articles:
            current_max = max_scores.get(article.source, 0)
            if article.score > current_max:
                max_scores[article.source] = article.score

        for article in self._articles:
            max_score = max_scores.get(article.source, 0)
            if max_score > 0:
                article.normalized_score = round((article.score / max_score) * 100, 1)
            else:
                article.normalized_score = 0.0

        ranked = sorted(
            self._articles,
            key=lambda a: (a.normalized_score, a.score),
            reverse=True,
        )

        if top_n is not None and top_n > 0:
            return ranked[:top_n]
        return ranked

    def __len__(self):
        return len(self._articles)

    def __iter__(self):
        return iter(self._articles)

    def __repr__(self):
        return f"<ArticleCollection: {len(self._articles)} articles>"