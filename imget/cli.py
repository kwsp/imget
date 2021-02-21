import argparse
import logging

from .main import main


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
