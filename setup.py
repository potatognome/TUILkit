from setuptools import setup, find_packages

setup(
    name="tUilKit",  # Make sure this name is unique on PyPI
    author="Daniel Austin",
    version="0.7.1",
    author_email="the.potato.gnome@gmail.com",
    description="A toolkit with utility functions for colour coding text output in a terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/tUilKit/",
    packages=find_packages(where="src") + ["tests"],  # Add "tests" if you want to distribute tests
    include_package_data=True,  # Include files specified in MANIFEST.in
    package_data={
        "tUilKit.config": ["*.json", "*.txt"],
        "tUilKit.dict": ["*.txt"],
        "tUilKit.interfaces": ["*.txt"],
        "tUilKit.utils": ["*.txt"],
        "tUilKit": ["*.txt"],
    },
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "fuzzywuzzy",
        "pyyaml",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
