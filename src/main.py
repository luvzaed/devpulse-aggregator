import argparse
import asyncio
from models import ArticleCollection
from database import DatabaseConnection, stream_db_data
from fetchers import GitHubFetcher, DevToFetcher
from exporter import generate_markdown_digest


def parse_args():
    parser = argparse.ArgumentParser(description="DevPulse Aggregator CLI")
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Limit output to the top N ranked articles across all sources",
    )
    return parser.parse_args()


async def fetch_and_store():
    fetchers = [GitHubFetcher(), DevToFetcher()]
    tasks = [fetcher.fetch() for fetcher in fetchers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    feed = ArticleCollection()
    for res in results:
        if not isinstance(res, Exception):
            for article in res:
                feed.add(article)

    with DatabaseConnection() as db:
        saved_count = 0
        for article in feed:
            db.save_article(article)
            saved_count += 1
            
    print(f"Successfully processed {saved_count} fetched articles into SQLite.")


if __name__ == "__main__":
    args = parse_args()

    # 1. Fetch latest items and persist to DB
    asyncio.run(fetch_and_store())
    
    # 2. Stream stored articles back out via generator
    stored_feed = ArticleCollection()
    for article in stream_db_data():
        stored_feed.add(article)

    # 3. Rank and filter using --top N
    ranked_articles = stored_feed.get_ranked(top_n=args.top)

    # 4. Generate the formatted Markdown briefing
    digest_file = generate_markdown_digest(ranked_articles)
    print(f"\n[Digest] Morning briefing generated at: {digest_file}")