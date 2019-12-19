import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="Artificial Vorzious Comparitor",
    version="1.0.0",
    description="Tool built to compare edi files",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Thierry de Wit",
    author_email="thierry.de.wit@bartosz.nl",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["avgui"],
    include_package_data=True,
    install_requires=[
        "subprocess", "PIL"
    ],
    entry_points={"console_scripts": ["avgui=avgui.__main__:main"]},
)