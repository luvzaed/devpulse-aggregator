from pathlib import Path

# Dynamically resolves to your main 'devpulse-aggregator' root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# File Paths
DB_PATH = BASE_DIR / "trending_feed.db"
DIGEST_PATH = BASE_DIR / "digest.md"

# Fetcher Configuration
TOPIC_TAG = "python"
ITEMS_PER_SOURCE = 5
MAX_RETRIES = 2
RETRY_DELAY = 1