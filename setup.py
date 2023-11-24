import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "work_set_clustering",
    version = "0.2.0",
    author = "Sven Lieber",
    author_email = "Sven.Lieber@kbr.be",
    description = ("A Python script to perform a clustering based on descriptive keys."),
    license = "AGPL-3.0",
    keywords = "FRBRization FRBR work-set-clustering",
    packages=setuptools.find_packages(),
    long_description=read('README.md')
)
