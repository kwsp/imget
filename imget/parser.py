from typing import Tuple, List
import logging
import urllib.parse
import sys

from bs4 import BeautifulSoup  # HTML Parser


SUFFIXES = ("jpg", "jpeg", "png", "gif")


def clean_url(url: str) -> str:
    """
    Remove query string from url

    """
    parse_res = urllib.parse.urlparse(url)
    parse_res = parse_res._replace(query="")
    url = parse_res.geturl()
    return url


def parse_html(
    html: str,
    class_=None,
    id_=None,
    tags_="a,img",
) -> Tuple[str, List[str]]:
    """
    Arguments:
        html - (str) HTML source to parse
        class_ - (str) CSS class name of the main content,
            defaults to entry-content
        id_ - (str) HTML id of main element

    Returns:
        img_links - (list[]) list of img links
    """
    # Get tags
    tags = tags_.split(",")

    # Parse with bs4. lxml backend is faster than html.parse
    logging.debug("Parsing HTML page...")
    soup = BeautifulSoup(html, "lxml")

    # If after filtering by class_, soup_ is not empty
    # set soup to soup_
    if class_:
        logging.debug(f"Matching by CSS class: {class_}")
        soup_ = soup.select(f".{class_}")
        if soup_:
            soup = soup_[0]
        else:
            logging.warning(
                f"Warning: class {class_} did not match any elements, ignoring."
            )

    # If after filtering by id_, soup_ is not empty
    # set soup to soup_
    if id_:
        logging.debug(f"Matching by id: {id_}")
        soup_ = soup.select(f"#{id_}")
        if soup_:
            soup = soup_
        else:
            logging.warning(
                f"Warning: id '{id_}' did not match any elements, ignoring."
            )

    img_links = []
    for _tag in tags:
        logging.info("Validating img and a tags")
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
        logging.warning("Warning: No image links were found.")
        sys.exit(1)

    # Simple validation
    img_links = [clean_url(l) for l in img_links if l.startswith("http")]

    n_list_before = len(img_links)
    # Remove duplicates
    img_links = list(set(img_links))
    n_list_after = len(img_links)

    logging.debug(
        f"Parsing complete, found, {len(img_links)} image links, removed {n_list_after - n_list_before} duplicates."
    )
    return img_links
