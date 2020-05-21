"""
Download images from the main content of a website
"""
import argparse
import os
import sys
import re
from pathlib import Path
from typing import List, Tuple
from urllib.request import urlretrieve
from urllib.parse import urlparse

from bs4 import BeautifulSoup  # HTML Parser
import requests
from tqdm import tqdm  # Progress bar

ERROR_LOG_FILE = "imget_error.txt"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0"
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
    parse_res = parse_res._replace(query=None)
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
        if img_tag and a_tag.get("href").endswith(SUFFIXES):
            img_links.append(a_tag.get("href"))
        else:
            img_links.append(img_tag.get("src"))

    if not img_links:
        print("Warning: No image links were found.")
        sys.exit(1)

    # Simple validation
    img_links = [l for l in img_links if l.startswith("http")]

    return title, img_links


def _mkdir(name: str) -> Path:
    """
    Create new directory with name given by 'name'.
    If directory exists, exit the program.

    Arguments:
        name - (str) relative or absolute path
    """
    # Create directory
    _dir = Path(name)
    _dir.mkdir(parents=True, exist_ok=False)
    return _dir.absolute()


def download_url_list(urls: List[str], out_dir: str):
    """
    Download url list to target directory
    """
    # Download all image img_links to new directory
    print(f"Downloading {len(urls)} files . . .")
    for url in tqdm(urls):
        basename = url.split("/")[-1]
        out_path = os.path.join(out_dir, basename)

        # Download and write image
        try:
            urlretrieve(url, out_path)
        except Exception as err:
            e_str = str(err)
            log_ = f"Error: {e_str}\n"
            print(log_)
            with open(ERROR_LOG_FILE, "a+") as file_handle:
                file_handle.write(log_)
    print(f"Downloaded {len(urls)} files.")


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


def _usage():
    exec_name = Path(sys.argv[0]).name
    print(f"Usage: {exec_name} [Options]... [URL]")


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
