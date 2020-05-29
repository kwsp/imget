"""
Download images from the main content of a website
"""
import argparse
import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

from tqdm import tqdm  # Progress bar

from .parser import parse_url_target
from .download import download_url_list

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


def main(url: str, out_dir: str = None, class_: str = None, id_: str = None):
    """
    Main code
    """
    print("\nDownloading and parsing HTML . . .")
    title, img_links = parse_url_target(url, class_=class_, id_=id_)

    # Create new dir with out_dir if specified
    if out_dir:
        try:
            out_dir = _mkdir(out_dir)
        except FileExistsError:
            # Fall back to page title as dir name
            print(
                f"Creating destination dir {out_dir} failed, using page title as out dir instead."
            )

    # Create new dir with title
    if not out_dir:
        try:
            out_dir = _mkdir(title)
        except FileExistsError:
            print("Cannot create output directory.")
            sys.exit(1)

    print(f"Downloading to directory {out_dir}")
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
    parser.add_argument("url", metavar="url", help="URL of HTML page")

    args = parser.parse_args()

    main(url=args.url, out_dir=args.out, class_=args.cls, id_=args.id)


if __name__ == "__main__":
    breakpoint()
