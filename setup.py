#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

test_requirements = ["pytest", "pytest-cov", "pytest-mock", "coverage"]

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open(os.path.join(here, "requirements.txt")) as f:
    install_requires = [line for line in f.readlines()]

setup(
    version_config=True,
    setup_requires=["setuptools-git-versioning", "pytest-runner"],
    name="gmail-wrapper",
    description="Because scrapping Gmail data doesn't have to be a pain",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Loadsmart Inc.",
    author_email="engineering@loadsmart.com",
    url="https://github.com/loadsmart/gmail-wrapper",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    keywords=["gmail"],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
