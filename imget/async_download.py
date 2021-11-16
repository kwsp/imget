#!/usr/bin/env python3
"""Asynchronously download a list of links."""

from typing import List, Iterable, Optional
import asyncio
import logging
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


async def _download_link(
    file: pathlib.Path, url: str, session: ClientSession, chunk_size=65536, **kwargs
) -> None:
    """GET request wrapper to download file

    kwargs are passed to `session.request()`.
    """
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)

    async with aiofiles.open(file, "wb") as fd:
        while True:
            chunk = await resp.content.read(chunk_size)
            if not chunk:
                break
            await fd.write(chunk)


async def _bulk_download_and_write(
        outdir: pathlib.Path, urls: Iterable[str], fnames: Optional[List[str]], **kwargs
) -> None:
    """Concurrently download multiple `urls` to `outdir`."""
    async with ClientSession() as session:
        tasks = []
        if not fnames:
            fnames = [url.split("/")[-1] for url in urls]

        for url, fname in zip(urls, fnames):
            tasks.append(
                _download_link(file=(outdir / fname), url=url, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)


def bulk_download(outdir: pathlib.Path, urls: Iterable[str], fnames: Optional[List[str]]=None, **kwargs) -> None:
    """Sync interface to asynchronously download multiple `urls` to `outdir`. kwargs are passed to aiohttp session.request."""
    assert sys.version_info >= (3, 7), "Asyncio requires Python 3.7+."

    asyncio.run(_bulk_download_and_write(outdir=outdir, urls=urls, fnames=fnames, **kwargs))


if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent

    with open(here.joinpath("links.txt")) as infile:
        urls = set(map(str.strip, infile))

    outpath = here.joinpath("new_dir")
    outpath.mkdir()
    bulk_download(outpath, urls)
