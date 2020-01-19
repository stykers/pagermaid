""" Packaging of PagerMaid. """

import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pagermaid",
    version="2020.1",
    author="Stykers",
    author_email="stykers@stykers.moe",
    description="A telegram utility daemon.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://katonkeyboard.moe/pagermaid.html",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix"
    ],
    python_requires=">=3.6"
)
