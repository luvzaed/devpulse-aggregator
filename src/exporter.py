from datetime import datetime
from pathlib import Path
from models import Article
from config import DIGEST_PATH, TOPIC_TAG


def generate_markdown_digest(
    articles: list[Article],
    output_path: Path | str = DIGEST_PATH,
) -> Path:
    """Writes a clean Markdown morning briefing from ranked Article objects."""
    path = Path(output_path)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# ☕ DevPulse Morning Briefing",
        f"**Generated:** {now_str} | **Topic:** `{TOPIC_TAG}` | **Items:** {len(articles)}",
        "",
        "---",
        "",
    ]

    if not articles:
        lines.append("*No trending articles found.*")
    else:
        for rank, article in enumerate(articles, start=1):
            metric_label = "⭐ Stars" if article.source == "GitHub" else "❤️ Reactions"
            clean_snippet = article.snippet.replace("\n", " ").strip()
            if len(clean_snippet) > 160:
                clean_snippet = clean_snippet[:157] + "..."

            lines.extend([
                f"### {rank}. [{article.title}]({article.url})",
                f"- **Source:** {article.source} (by `@{article.author}`)",
                f"- **Score:** {article.score:,} {metric_label} *(Normalized: {article.normalized_score}/100)*",
                f"- **Summary:** {clean_snippet}",
                "",
            ])

    path.write_text("\n".join(lines), encoding="utf-8")
    return path