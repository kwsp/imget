from urllib.parse import urlparse
from typing import Tuple, List
import requests
import sys

from bs4 import BeautifulSoup  # HTML Parser


SUFFIXES = ("jpg", "jpeg", "png", "gif")


def parse_url_target(url: str, class_=None, id_=None) -> Tuple[str, List[str]]:
    """
    Arguments:
        url - (str) URL of the page to parse. This function
            uses BeautifulSoup to parse the main content of
            the page to get all image links.
        class_ - (str) CSS class name of the main content,
            defaults to entry-content
        id_ - (str) HTML id of main element

    Returns:
        title - (str) Page title
        img_links - (list[]) list of img links
    """
    # Preprocess URL
    if not url.startswith("http"):
        url = "http://" + url

    parse_res = urlparse(url)
    # Remove query string
    parse_res = parse_res._replace(query="")
    url = parse_res.geturl()

    # Get initial url
    resp = requests.get(url)

    # Parse with bs4. lxml backend is faster than html.parse
    soup = BeautifulSoup(resp.text, "lxml")

    # Get title for new dir name
    title = soup.title.string

    # If after filtering by class_, soup_ is not empty
    # set soup to soup_
    if class_:
        soup_ = soup.select(f".{class_}")
        if soup_:
            soup = soup_[0]
        else:
            print(f"Warning: class {class_} did not match any elements, ignoring.")

    # If after filtering by id_, soup_ is not empty
    # set soup to soup_
    if id_:
        soup_ = soup.select(f"#{id_}")
        if soup_:
            soup = soup_
        else:
            print(f"Warning: id '{id_}' did not match any elements, ignoring.")

    # Get all a tags with img tags inside, and their links
    a_tags = soup.select("a[href]")
    img_links = [
        t.get("href")
        for t in a_tags
        if t.findChild("img") and t.get("href").endswith(SUFFIXES)
    ]
    for a_tag in a_tags:
        img_tag = a_tag.findChild("img")
        if img_tag:
            if a_tag.get("href").endswith(SUFFIXES):
                img_links.append(a_tag.get("href"))
            else:
                img_links.append(img_tag.get("src"))

    if not img_links:
        print("Warning: No image links were found.")
        sys.exit(1)

    # Simple validation
    img_links = [l for l in img_links if l.startswith("http")]

    return title, img_links

