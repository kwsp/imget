from typing import List
import logging
import urllib.error
import urllib.parse

from bs4 import BeautifulSoup  # HTML Parser

logger = logging.getLogger(__name__)

IMG_TYPES = ("jpg", "jpeg", "png", "gif", "webp")


def clean_url(url: str) -> str:
    "Remove query string from url"
    parse_res = urllib.parse.urlparse(url)
    parse_res = parse_res._replace(query="")
    url = parse_res.geturl()
    return url


def best_srcset(srcset: str) -> str:
    """Get the highest resolution link from srcset
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attr-srcset
    """
    best_link = ""
    best_w_or_x = 0
    for pair in srcset.split(","):
        link, size = pair.strip().split()
        # Assume the website implements srcset correctly
        # using either 'w' (width) or 'x' (pixel density)
        try:
            size_i = int(size[:-1])
        except ValueError:
            logger.exception("failed to parse srcset: %s", srcset)
            return ""
        else:
            if size_i > best_w_or_x:
                best_link = link
                best_w_or_x = size_i

    return best_link


def parse_html(
    html: str,
    url: str = "",
    class_: str = "",
    id_: str = "",
    tags_: str = "a,img",
) -> List[str]:
    """
    Arguments:
        html - HTML source to parse
        url - URL of page, helps with parsing relative links
        class_ - CSS class name of the main content,
        id_ - HTML id of main element

    Returns:
        img_links - (list[]) list of img links
    """
    tags_to_check = tags_.split(",")
    soup = BeautifulSoup(html, "lxml")

    # If after filtering by class_, soup_ is not empty, set soup to soup_
    if class_:
        logger.debug("matching by CSS class: %s", class_)
        soup_ = soup.select(f".{class_}")
        if soup_:
            soup = soup_[0]
        else:
            logger.debug("class %s did not match any elements, ignoring.", class_)

    # If after filtering by id_, soup_ is not empty, set soup to soup_
    if id_:
        logger.debug("matching by id: %s", id_)
        soup_ = soup.select(f"#{id_}")
        if soup_:
            soup = soup_[0]
        else:
            logger.debug("id '%s' did not match any elements, ignoring.", id_)

    img_links = set()

    def add_valid_link(url: str, link: str):
        try:
            abslink = urllib.parse.urljoin(url, link)
        except (urllib.error.URLError, ValueError):
            logger.exception("error parsing URL: %s", link)
            pass
        else:
            img_links.add(abslink)

    # Check all 'a' tags that contain an 'img' tag within. Sometimes the
    # highest resolution images are linked by the 'a' tag.
    if "a" in tags_to_check:
        for a_tag in soup.select("a[href]"):
            img_tag = a_tag.findChild("img")
            link = a_tag.get("href")
            if link and img_tag and link.endswith(IMG_TYPES):
                add_valid_link(url, link)

    # Check 'img' tags themselves. First check the 'data-srcset' and 'srcset',
    # parsing them to get the highest resolution available. If neither are
    # available, fall back to 'src'
    if "img" in tags_to_check:
        for img_tag in soup.select("img"):
            link = None

            if img_tag.get("data-srcset"):
                link = best_srcset(img_tag.get("data-srcset"))
            elif img_tag.get("srcset"):
                link = best_srcset(img_tag.get("srcset"))
            else:
                link = img_tag.get("src")

            if link:
                add_valid_link(url, link)

    if not img_links:
        logger.debug("no image links were found.")
        return []

    logger.debug("parsing complete, found, %s image links.", len(img_links))
    return list(img_links)
