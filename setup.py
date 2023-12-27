#!/usr/bin/env python
from setuptools import setup, find_packages

requirements = [
    "requests>2,<3",
    "google-auth-httplib2<1",
    "google-api-python-client>1,<2",
    "google-auth>1,<2",
]
test_requirements = ["pytest", "pytest-cov", "pytest-mock", "coverage"]

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

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
    install_requires=requirements,
    keywords=["gmail"],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)
