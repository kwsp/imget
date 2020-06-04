"""
Download images from the main content of a website
"""
from pathlib import Path
from typing import List, Tuple
import argparse
import logging
import os
import re
import sys

from .parser import parse_url_target
from .download import download_url_list
from .logger import get_logger, init_logger

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
    id_: str = None,
    log_level=logging.DEBUG,
):
    """
    Main code
    """
    init_logger(log_level)

    get_logger().info("Downloading and parsing HTML . . .")
    title, img_links = parse_url_target(url, class_=class_, id_=id_)

    # Create new dir with out_dir if specified
    if out_dir:
        try:
            get_logger().debug(f"Trying to create provided out dir: {out_dir}")
            out_dir = _mkdir(out_dir)
        except FileExistsError:
            # Fall back to page title as dir name
            get_logger().error(
                f"Creating destination dir {out_dir} failed, using page title as out dir instead."
            )

    # Create new dir with title
    if not out_dir:
        try:
            get_logger().debug(f"Trying to create out dir with title: {title}")
            out_dir = _mkdir(title)
        except FileExistsError:
            get_logger().error("Cannot create output directory.")
            sys.exit(1)

    get_logger().info(f"Downloading to directory {out_dir}")
    download_url_list(img_links, out_dir)


def entry_point():
    """
    Command line interface
    """
    parser = argparse.ArgumentParser(description="Download images from a HTML page.")
    parser.add_argument(
        "-c", "--cls", type=str, help="CSS class of main element", default=None
    )
    parser.add_argument(
        "-i", "--id", type=str, help="HTML id of main element", default=None
    )
    parser.add_argument("-o", "--out", type=str, help="Output directory", default=None)
    parser.add_argument(
        "-v", "--verbosity", action="count", help="Verbosity", default=0
    )
    parser.add_argument("url", metavar="url", help="URL of HTML page")

    args = parser.parse_args()

    log_level = logging.INFO if args.verbosity == 0 else logging.DEBUG

    main(
        url=args.url,
        out_dir=args.out,
        class_=args.cls,
        id_=args.id,
        log_level=log_level,
    )


if __name__ == "__main__":
    breakpoint()
