#!/usr/bin/env python3
"""Asynchronously download a list of links."""

from typing import Iterable
import asyncio
import logging
import mimetypes
import pathlib
import sys

import aiofiles
from aiohttp import ClientSession

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
logging.getLogger("chardet.charsetprober").disabled = True


async def download_link(
    file: pathlib.Path, url: str, session: ClientSession, chunk_size=65536, **kwargs
) -> None:
    """GET request wrapper to download file

    kwargs are passed to `session.request()`.
    """
    if file.exists():
        logger.info("File %s exist, skipping URL: %s", file, url)
        return
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)

    ctype = resp.headers["content-type"]

    async with aiofiles.open(file, "wb") as fd:
        while True:
            chunk = await resp.content.read(chunk_size)
            if not chunk:
                break
            await fd.write(chunk)


async def bulk_download_and_write(
    outdir: pathlib.Path, urls: Iterable[str], **kwargs
) -> None:
    """Concurrently download multiple `urls` to `outdir`."""
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            fname = url.split("/")[-1]
            tasks.append(
                download_link(file=(outdir / fname), url=url, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)


def bulk_download(outdir: pathlib.Path, urls: Iterable[str], **kwargs) -> None:
    """Sync interface to asynchronously download multiple `urls` to `outdir`. kwargs are passed to aiohttp session.request."""
    assert sys.version_info >= (3, 7), "Asyncio requires Python 3.7+."

    asyncio.run(bulk_download_and_write(outdir=outdir, urls=urls, **kwargs))


if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    with open(here.joinpath("links.txt")) as infile:
        urls = set(map(str.strip, infile))

    outpath = here.joinpath("new_dir")
    outpath.mkdir()
    bulk_download(outpath, urls)
