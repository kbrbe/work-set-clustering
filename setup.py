import os
import setuptools

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name = "work_set_clustering",
    version = "0.4.0",
    url = "https://github.com/kbrbe/work-set-clustering",
    author = "Sven Lieber",
    author_email = "Sven.Lieber@kbr.be",
    description = ("A Python script to perform a clustering based on descriptive keys."),
    license = "AGPL-3.0",
    keywords = "FRBRization FRBR work-set-clustering",
    packages=setuptools.find_packages(),
    long_description_content_type = "text/markdown",
    long_description=read('README.md')
)
