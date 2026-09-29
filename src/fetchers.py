import asyncio
import aiohttp
from abc import ABC, abstractmethod
from functools import wraps
from models import Article

# --- CUSTOM EXCEPTIONS ---
class AggregatorError(Exception):
    pass

class APIFetchError(AggregatorError):
    pass

# --- RETRY DECORATOR ---
def retry(max_retries=3, delay=1):
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
        self.url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"

    @retry(max_retries=2, delay=1)
    async def fetch(self) -> list[Article]:
        print("Starting GitHub fetch...")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise APIFetchError(f"GitHub API failed with status {response.status}")
                payload = await response.json()
                
                articles = []
                for item in payload.get("items", [])[:3]:
                    articles.append(Article(
                        source=self.source_name,
                        title=item.get("name", "Unknown"),
                        url=item.get("html_url", ""),
                        author=item.get("owner", {}).get("login", "Unknown"),
                        score=item.get("stargazers_count", 0)
                    ))
                print("Finished GitHub fetch!")
                return articles

class DevToFetcher(BaseFetcher):
    def __init__(self):
        super().__init__(source_name="Dev.to")
        self.url = "https://dev.to/api/articles?tag=python&per_page=3"

    @retry(max_retries=2, delay=1)
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
                        score=item.get("positive_reactions_count", 0)
                    ))
                print("Finished Dev.to fetch!")
                return articles