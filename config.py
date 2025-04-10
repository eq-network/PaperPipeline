"""
Configuration settings template for the BibTeX to Structured Text Pipeline

Copy this file to 'config.py' and customize the settings for your environment.
"""

# User information
# Used for API requests that require identification
USER_EMAIL = "your-email@example.com"  # CHANGE THIS to your actual email

# Paths
# Path to your Zotero storage directory (if you're using Zotero)
ZOTERO_BASE_DIR = "~/Zotero/storage"  # Adjust if your Zotero storage is elsewhere

# Network settings
# User agent for HTTP requests to avoid being blocked
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# API configuration
UNPAYWALL_API_EMAIL = USER_EMAIL  # Email for Unpaywall API
GROBID_DEFAULT_URL = "http://localhost:8070"  # Default GROBID server URL

# Processing settings
GROBID_RATE_LIMIT = 1  # Time to sleep between GROBID requests (seconds)
MAX_TITLE_LENGTH = 100  # Maximum length for filenames based on titles

# Retrieval sources configuration
# Enable/disable different PDF retrieval methods
RETRIEVAL_SOURCES = {
    "unpaywall": True,     # Retrieve PDFs using DOI via Unpaywall
    "arxiv": True,         # Retrieve PDFs from arXiv
    "semantic_scholar": True,  # Search for PDFs by title via Semantic Scholar
    "scihub": False,       # Use Sci-Hub as fallback (legal status varies by country)
}

# URLs for different services
# API endpoints and base URLs for the retrieval sources
SERVICE_URLS = {
    "unpaywall": "https://api.unpaywall.org/v2/",
    "arxiv": "https://arxiv.org/pdf/",
    "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search",
    "scihub": "https://sci-hub.se/",  # May need to be updated as the domain changes
}