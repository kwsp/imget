from distutils.core import setup

# Get version without importing
exec(compile(open("imget/version.py").read(), "imget/version.py", "exec"))

setup(
    name="imget",
    version=__version__,
    description="Command-line program and library for parsing and downloading images from the web.",
    author="Tiger Nie",
    author_email="nhl0819@gmail.com",
    url="https://github.com/NieTiger/imget",
    license="mit",
    packages=["imget"],
    python_requires=">=3.7",
    scripts=["bin/imget"],
    install_requires=["tqdm", "bs4", "lxml", "requests", "aiofiles", "aiohttp"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Multimedia :: Graphics",
    ],
)
