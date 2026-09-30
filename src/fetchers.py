import asyncio
import aiohttp
from abc import ABC, abstractmethod
from functools import wraps
from models import Article
from config import TOPIC_TAG, ITEMS_PER_SOURCE, MAX_RETRIES, RETRY_DELAY


# --- CUSTOM EXCEPTIONS ---
class AggregatorError(Exception):
    pass


class APIFetchError(AggregatorError):
    pass


# --- RETRY DECORATOR ---
def retry(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"  [!] Attempt {attempt}/{max_retries} failed for {func.__name__}: {e}")
                    if attempt == max_retries:
                        raise e
                    await asyncio.sleep(delay)
        return wrapper
    return decorator


# --- BASE FETCHER ---
class BaseFetcher(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    async def fetch(self) -> list[Article]:
        pass


class GitHubFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(source_name="GitHub")
        self.url = f"https://api.github.com/search/repositories?q=language:{TOPIC_TAG}&sort=stars&order=desc&per_page={ITEMS_PER_SOURCE}"

    @retry()
    async def fetch(self) -> list[Article]:
        print("Starting GitHub fetch...")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise APIFetchError(f"GitHub API failed with status {response.status}")
                payload = await response.json()
                
                articles = []
                for item in payload.get("items", [])[:ITEMS_PER_SOURCE]:
                    articles.append(Article(
                        source=self.source_name,
                        title=item.get("name", "Unknown"),
                        url=item.get("html_url", ""),
                        author=item.get("owner", {}).get("login", "Unknown"),
                        score=item.get("stargazers_count", 0),
                        snippet=item.get("description") or "No description available.",
                    ))
                print("Finished GitHub fetch!")
                return articles


class DevToFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(source_name="Dev.to")
        self.url = f"https://dev.to/api/articles?tag={TOPIC_TAG}&per_page={ITEMS_PER_SOURCE}"

    @retry()
    async def fetch(self) -> list[Article]:
        print("Starting Dev.to fetch...")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise APIFetchError(f"Dev.to API failed with status {response.status}")
                
                articles = []
                for item in await response.json():
                    articles.append(Article(
                        source=self.source_name,
                        title=item.get("title", "Unknown"),
                        url=item.get("url", ""),
                        author=item.get("user", {}).get("username", "Unknown"),
                        score=item.get("positive_reactions_count", 0),
                        snippet=item.get("description") or "No description available.",
                    ))
                print("Finished Dev.to fetch!")
                return articles