"""
Download helpers

"""
from concurrent.futures import ThreadPoolExecutor as Executor
from typing import List
from urllib.request import urlretrieve
import os


def _download_url(url: str, out_path: str):
    try:
        urlretrieve(url, out_path)
        print(f"Downloaded {url}")
    except Exception as err:
        e_str = str(err)
        log_ = f"Error: {e_str}\n"
        print(log_)


_counter = 0


def _get_filename(out_dir: str, basename: str):
    global _counter
    _counter += 1
    _, ext = os.path.splitext(basename)
    out_path = os.path.join(out_dir, str(_counter) + ext)
    return out_path


def download_url_list(urls: List[str], out_dir: str, max_workers=None):
    """
    Download url list to target directory concurrently
    using python threads
    """
    # Download all image urls to new directory
    print(f"Downloading {len(urls)} files . . .")

    with Executor(max_workers=max_workers) as exe:
        jobs = []
        for url in urls:
            basename = url.split("/")[-1]
            out_path = _get_filename(out_dir, basename)

            # Download and write image
            jobs.append(exe.submit(_download_url, url, out_path))

        # results = [job.result() for job in jobs]

    print(f"Downloaded {len(urls)} files.")

