from urllib.parse import urlparse
from typing import Tuple, List
import requests
import sys

from bs4 import BeautifulSoup  # HTML Parser

from .logger import get_logger


SUFFIXES = ("jpg", "jpeg", "png", "gif")


def _remove_query_string(url: str) -> str:
    """
    Remove query string from url

    """
    parse_res = urlparse(url)
    parse_res = parse_res._replace(query="")
    url = parse_res.geturl()
    return url


def parse_url_target(
    url: str, class_=None, id_=None, tags=["a", "img"]
) -> Tuple[str, List[str]]:
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
    get_logger().debug(f"Preprocessing URL, original: {url}")
    # Add HTTP if not
    if not url.startswith("http"):
        url = "http://" + url

    # Remove query string
    url = _remove_query_string(url)

    # Remove trailing slash
    url = url.strip("/")

    get_logger().debug(f"Preprocessing URL, final: {url}")

    # Get initial url
    get_logger().debug("Getting HTML page...")
    resp = requests.get(url)

    # Parse with bs4. lxml backend is faster than html.parse
    get_logger().debug("Parsing HTML page...")
    soup = BeautifulSoup(resp.text, "lxml")

    # Get title for new dir name
    # HTML pge title is often a bad name for a directory, so
    # we'll use the last section of the url
    title = url.split("/")[-1]

    # If after filtering by class_, soup_ is not empty
    # set soup to soup_
    if class_:
        get_logger().debug(f"Matching by CSS class: {class_}")
        soup_ = soup.select(f".{class_}")
        if soup_:
            soup = soup_[0]
        else:
            get_logger().warning(
                f"Warning: class {class_} did not match any elements, ignoring."
            )

    # If after filtering by id_, soup_ is not empty
    # set soup to soup_
    if id_:
        get_logger().debug(f"Matching by id: {id_}")
        soup_ = soup.select(f"#{id_}")
        if soup_:
            soup = soup_
        else:
            get_logger().warning(
                f"Warning: id '{id_}' did not match any elements, ignoring."
            )

    img_links = []
    for _tag in tags:
        get_logger().info("Validating img and a tags")
        #
        # Check all 'a' tags that contain an 'img' tag within. Sometimes the
        # highest resolution images are linked by the 'a' tag.
        #
        if _tag == "a":
            # Get all a tags with img tags inside, and their links
            a_tags = soup.select("a[href]")
            img_links.extend(
                [
                    t.get("href")
                    for t in a_tags
                    if t.findChild("img") and t.get("href").endswith(SUFFIXES)
                ]
            )
            for a_tag in a_tags:
                img_tag = a_tag.findChild("img")
                if img_tag:
                    if a_tag.get("href").endswith(SUFFIXES):
                        img_links.append(a_tag.get("href"))
                    elif img_tag.get("src"):
                        img_links.append(img_tag.get("src"))
        #
        # Check 'img' tags themselves. First check the 'data-srcset' and 'srcset',
        # parsing them to get the highest resolution available. If neither are
        # available, fall back to 'src'
        #
        elif _tag == "img":
            img_tags = soup.select("img")
            for img_tag in img_tags:
                good_link = None

                if img_tag.get("data-srcset"):
                    _links = img_tag.get("data-srcset")
                    good_link = _links.split(",")[-1].strip().split(" ")[0]

                if not good_link and img_tag.get("srcset"):
                    _links = img_tag.get("srcset")
                    good_link = _links.split(",")[-1].strip().split(" ")[0]

                if not good_link:
                    good_link = img_tag.get("src")

                if good_link:
                    img_links.append(good_link)

    if not img_links:
        get_logger().warning("Warning: No image links were found.")
        sys.exit(1)

    # Simple validation
    img_links = [_remove_query_string(l) for l in img_links if l.startswith("http")]

    get_logger().debug(f"Parsing complete, found, {len(img_links)} image links.")
    return title, img_links

