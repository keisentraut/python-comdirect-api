from setuptools import setup

from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="comdirect_api",
    version="0.1",
    description="Python module for comdirect REST api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keisentraut/python-comdirect-api",
    author="Klaus Eisentraut",
    author_email="klaus-python-comdirect-api@hohenpoelz.de",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="comdirect rest api",
    packages=["comdirect_api"],
    python_requires=">=3.6",
    install_requires=[
# TODO: I am not sure if those packages are installed by default or not.
# For now, I just uncommented them, too lazy for a proper test...
#        "base64",
        "datetime",
#        "decimal",
#        "io",
#        "json",
        "pillow",
        "requests",
#        "time",
        "uuid",
    ],
    project_urls={
        "Bug Reports": "https://github.com/keisentraut/python-comdirect-api/issues",
        # 'Funding': 'https://donate.pypi.org',
        # 'Say Thanks!': 'http://saythanks.io/to/example',
        "Source": "https://github.com/keisentraut/python-comdirect-api/",
    },
)
