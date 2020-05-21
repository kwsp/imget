"""
Download images from the main content of a website
"""
import argparse
import sys
from pathlib import Path
from typing import List, Tuple
from urllib.request import urljoin, urlopen, urlretrieve

from bs4 import BeautifulSoup  # HTML Parser
from tqdm import tqdm  # Progress bar

SUFFIXES = (".jpg", ".jpeg", ".png")


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
    if not url.startswith("http"):
        url = "http://" + url
    # Parse with bs4
    soup = BeautifulSoup(urlopen(url), "lxml")

    # Get title for new dir name
    title = soup.title.string

    # If after filtering by class_, soup_ is not empty
    # set soup to soup_
    if class_:
        soup_ = soup.find("div", class_=class_)
        if soup_:
            soup = soup_
        else:
            print(f"Warning: class {class_} did not match any elements, ignoring.")

    # If after filtering by id_, soup_ is not empty
    # set soup to soup_
    if id_:
        soup_ = soup.find(id=id_)
        if soup_:
            soup = soup_
        else:
            print(f"Warning: id '{id_}' did not match any elements, ignoring.")

    # Get all image links
    img_tags = soup.select("img[src]")

    if not img_tags:
        print(f"Warning: No image links were found.")
        sys.exit(1)

    img_links = [t.get("src") for t in img_tags]

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
    return _dir


def main(url: str, out_dir: str = None, class_: str = None, id_: str = None):
    """
    Main code
    """
    print(f"Downloading and parsing HTML...")
    # Parse URL target
    title, img_links = parse_url_target(url)

    # Create new dir with out_dir if specified
    if out_dir:
        try:
            out_dir = _mkdir(out_dir)
        except FileExistsError:
            print(
                f"Creating destination dir {out_dir} failed, using page as out dir instead."
            )

    # Create new dir with title
    if not out_dir:
        try:
            out_dir = _mkdir(title)
        except FileExistsError:
            print(f"Cannot create output directory.")
            sys.exit(1)

    print(f"Downloading to directory {out_dir.resolve()}")
    # Download all image img_links to new directory
    for link in tqdm(img_links):
        basename = Path(link).name
        out_path = out_dir / basename
        # Download and write image
        urlretrieve(link, out_path)

    print(f"Downloaded {len(img_links)} files.")


def _usage():
    exec_name = Path(sys.argv[0]).name
    print(f"Usage: {exec_name} [Options]... [URL]")


def entry_point():
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
