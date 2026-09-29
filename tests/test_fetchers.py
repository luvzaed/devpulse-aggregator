import pytest
import sys
import os
from unittest.mock import patch, AsyncMock

# Add the 'src' folder to Python's path so it can find our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fetchers import GitHubFetcher

# The asyncio marker tells pytest this is an asynchronous test
@pytest.mark.asyncio
# We patch aiohttp's get method so it never actually hits the real internet
@patch("aiohttp.ClientSession.get")
async def test_github_fetcher_success(mock_get):
    # 1. Setup the fake API response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "items": [
            {
                "name": "test-portfolio",
                "html_url": "https://github.com/mock/test-portfolio",
                "owner": {"login": "Zaid"},
                "stargazers_count": 9999
            }
        ]
    }
    
    # 2. Trick the 'async with' context manager into using our fake response
    mock_get.return_value.__aenter__.return_value = mock_response

    # 3. Run the actual fetcher
    fetcher = GitHubFetcher()
    result = await fetcher.fetch()

    # 4. Assert that our code processed the fake data correctly
    assert len(result) == 1
    assert result[0].title == "test-portfolio"
    assert result[0].author == "Zaid"
    assert result[0].score == 9999