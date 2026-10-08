import requests
from bs4 import BeautifulSoup

#Extract main article of news link
def get_article_html(url):
    #Try to extract details from url if defined time
    response = requests.get(
        url,
        timeout=10,
    )

    #Raise an exception for HTTP errors
    response.raise_for_status()

    return response.text


def extract_article_text(html, url):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # Each news website uses a different HTML structure
    if "varzesh3.com" in url:
        selector = "div.news-body"

    elif "khabarvarzeshi.com" in url:
        selector = "div.item-text"

    elif "kayhanvarzeshi.ir" in url:
        selector = "div.body"

    else:
        return None

    article = soup.select_one(selector)

    # The expected article container was not found.
    if article is None:
        return None

    #Convert the HTML content into clean plain text.
    return article.get_text(
        "\n",
        strip=True,
    )