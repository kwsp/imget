"""
Download images from the main content of a website
"""
from typing import List, Tuple
import argparse
import logging
import os
import sys
import pathlib
import requests

from .async_download import bulk_download
from .parser import clean_url, parse_html

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0"

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("imget")

logging.getLogger("chardet.charsetprober").disabled = True
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3").propagate = False


def _mkdir(name: str) -> pathlib.Path:
    "Create new directory with `name`."
    # Create directory
    _dir = pathlib.Path(name)
    _dir.mkdir(parents=True, exist_ok=True)
    return _dir


def main(
    url: str,
    out_dir: str = "",
    class_: str = "",
    tags_: str = "a,img,video",
    id_: str = "",
    log_level=logging.INFO,
    listonly: bool = False,
):
    "Main code"
    logger.setLevel(log_level)

    # Preprocess URL
    logger.debug("Preprocessing URL, original: %s", url)
    url = clean_url(url)  # Remove query string
    url = url.strip("/")  # Remove trailing slash
    logger.debug("Preprocessing URL, final: %s", url)

    # Get initial url
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers)
        logger.info("Got response [%s] for URL: %s", resp.status_code, url)
    except requests.HTTPError as e:
        logger.exception("requests exception for URL: %s", url)
        logger.exception(e)
        sys.exit(1)

    # Get title for new dir name
    title = url.split("/")[-1]
    img_links = parse_html(resp.text, class_=class_, id_=id_, tags_=tags_)

    if listonly:
        # Return the list of links found and exit
        for link in img_links:
            print(link)
        sys.exit(0)

    # Create new dir with out_dir or title and download
    if out_dir:
        outpath = _mkdir(out_dir)
    elif title:
        outpath = _mkdir(title)
    else:
        logger.error("Please provide a output directory")
        sys.exit(1)

    bulk_download(outpath, img_links, headers=headers)
