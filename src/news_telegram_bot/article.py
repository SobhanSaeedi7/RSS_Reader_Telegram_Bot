import requests
from bs4 import BeautifulSoup


def get_article_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.text


def extract_article_text(html):
    soup = BeautifulSoup(html, "html.parser")

    article = soup.select_one("div.news-body")

    if article is None:
        return None

    return article.get_text("\n", strip=True)