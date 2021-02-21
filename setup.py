from distutils.core import setup

setup(
    name="imget",
    version="0.1.0",
    description="CLI that downloads images from the main content of a target URL",
    author="Tiger Nie",
    packages=["imget"],
    scripts=["bin/imget"],
    install_requires=["tqdm", "bs4", "lxml", "requests", "aiofiles", "aiohttp"],
)
