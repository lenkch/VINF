import requests
import os
import re

os.makedirs("data/raw", exist_ok=True)

# --- site-specific configuration ---
START_URL = "https://www.themoviedb.org/person/10859-ryan-reynolds"

ALLOWED_URL_PATTERN = (
    r"^https://www\.themoviedb\.org/person/"
    r"[0-9]+-[a-zA-Z0-9-]+/?$"
)

USER_AGENT = (
    "lc-vinf-themoviedb-crawler"
)

DELAY_SECONDS = 2
REQUEST_TIMEOUT = 10
# -----------------------------------

def fetch(url):
    response = requests.get(
        url,
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    },
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return response


def main():
    response = fetch(START_URL)

    movie_links = re.findall(
        r'href="(/movie/[0-9]+-[a-zA-Z0-9-]+)"',
        response.text
    )

    print(movie_links)


if __name__ == "__main__":
    main()