"""
Download images from the main content of a website
"""
import argparse
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
import requests

from .download import download_url_list
from .parser import clean_url, parse_html

ERROR_LOG_FILE = "imget_error.txt"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0"


def _mkdir(name: str) -> str:
    """
    Create new directory with name given by 'name'.
    If directory exists, exit the program.

    Arguments:
        name - (str) relative or absolute path
    """
    # Create directory
    _dir = Path(name)
    _dir.mkdir(parents=True, exist_ok=False)
    return _dir.resolve().as_posix()


def main(
    url: str,
    out_dir: str = None,
    class_: str = None,
    tags_: str = "a,img",
    id_: str = None,
    log_level=logging.DEBUG,
    listonly: bool = False,
):
    """
    Main code
    """
    logging.basicConfig(level=log_level)

    # Preprocess URL
    logging.debug(f"Preprocessing URL, original: {url}")
    # Add HTTP if not
    if not url.startswith("http"):
        url = "http://" + url

    # Remove query string
    url = clean_url(url)

    # Remove trailing slash
    url = url.strip("/")

    logging.debug(f"Preprocessing URL, final: {url}")

    # Get initial url
    logging.debug("Getting HTML page...")
    resp = requests.get(url)

    # Get title for new dir name
    # HTML pge title is often a bad name for a directory, so
    # we'll use the last section of the url
    title = url.split("/")[-1]

    img_links = parse_html(resp.text, class_=class_, id_=id_, tags_=tags_)

    if listonly:
        # Return the list of links found and exit
        for link in img_links:
            print(link)
        sys.exit(0)

    # Create new dir with out_dir if specified
    if out_dir:
        try:
            logging.debug(f"Trying to create provided out dir: {out_dir}")
            out_dir = _mkdir(out_dir)
        except FileExistsError:
            # Fall back to page title as dir name
            logging.error(
                f"Creating destination dir {out_dir} failed, using page title as out dir instead."
            )

    # Create new dir with title
    if not out_dir:
        try:
            logging.debug(f"Trying to create out dir with title: {title}")
            out_dir = _mkdir(title)
        except FileExistsError:
            logging.error("Cannot create output directory.")
            sys.exit(1)

    logging.info(f"Downloading to directory {out_dir}")
    download_url_list(img_links, out_dir)


def entry_point():
    """
    Command line interface
    """
    parser = argparse.ArgumentParser(
        description="Download images linked from a HTML page."
    )
    parser.add_argument(
        "-c",
        "--cls",
        type=str,
        help="CSS class of main element to constrain image search.",
        default=None,
    )
    parser.add_argument(
        "-i",
        "--id",
        type=str,
        help="HTML id of main element to constrain image search.",
        default=None,
    )
    parser.add_argument(
        "-t",
        "--tags",
        type=str,
        help='HTML tag to find image links. If multiple, give them in a comma separated string, e.g. "a,img".',
        default="a,img",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        help="Output directory, defaults to url basename.",
        default=None,
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", help="Verbosity.", default=0
    )
    parser.add_argument(
        "-l",
        "--list",
        dest="listonly",
        action="store_true",
        help="Return the list of image links and exit",
    )
    parser.set_defaults(listonly=False)
    parser.add_argument("url", metavar="url", help="URL of HTML page.")

    args = parser.parse_args()

    log_level = logging.INFO if args.verbosity == 0 else logging.DEBUG

    main(
        url=args.url,
        out_dir=args.out,
        class_=args.cls,
        tags_=args.tags,
        id_=args.id,
        log_level=log_level,
        listonly=args.listonly,
    )


if __name__ == "__main__":
    breakpoint()
