import asyncio
from models import ArticleCollection
from database import DatabaseConnection, stream_db_data
from fetchers import GitHubFetcher, DevToFetcher

async def main():
    fetchers = [GitHubFetcher(), DevToFetcher()]
    tasks = [fetcher.fetch() for fetcher in fetchers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    feed = ArticleCollection()
    for res in results:
        if not isinstance(res, Exception):
            for article in res:
                feed.add(article)

    # Database Handling using our Context Manager
    with DatabaseConnection("trending_feed.db") as db:
        saved_count = 0
        for article in feed:
            db.save_article(article)
            saved_count += 1
            
    print(f"Successfully passed {saved_count} articles to SQLite database.")


if __name__ == "__main__":
    asyncio.run(main())
    
    print("\n--- Reading back from Database using a Generator ---")
    row_generator = stream_db_data("trending_feed.db")
    
    for count, row in enumerate(row_generator, start=1):
        source, title, author = row
        print(f"Streamed row {count}: {title[:30]}... from {source} by @{author}")