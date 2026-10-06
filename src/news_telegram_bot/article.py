import requests
from bs4 import BeautifulSoup


def get_article_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def extract_article_text(html, url):
    soup = BeautifulSoup(html, "html.parser")

    if "varzesh3.com" in url:
        selector = "div.news-body"

    elif "khabarvarzeshi.com" in url:
        selector = "div.item-text"

    elif "kayhanvarzeshi.ir" in url:
        selector = "div.body"

    else:
        return None

    article = soup.select_one(selector)

    if article is None:
        return None

    return article.get_text("\n", strip=True)