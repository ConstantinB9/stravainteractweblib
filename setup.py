#!/usr/bin/env python

from setuptools import setup
import os.path


try:
    DIR = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(DIR, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = None


setup(
    name="stravainteractweblib",
    version="0.0.1",
    description=" Extends the Strava v3 API using web scraping and web browser interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ConstantinB9/stravainteractweblib",
    license="MPLv2",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ],
    packages=["stravainteractweblib"],
    python_requires=">=3.4.0",
    install_requires=[
        "stravaweblib>=0.0.6",
        "selenium>=4.3.0",
    ],
)