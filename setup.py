#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="tsp",
    version="1.0.0",
    description=(
        "Tools for researching relations between the TSP and proximity graphs."
    ),
    author="Logan Graham, Gaurish Telang, and Sam van der Poel",
    url="https://github.com/samvanderpoel/TSP-vs-Graphs",
    packages=find_packages(),
    install_requires=[
        "black",
        "Cython",
        "ipython",
        "matplotlib",
        "maturin",
        "networkx",
        "numpy",
        "pyyaml",
        "scikit-learn",
        "scipy",
        "setuptools-rust",
        "termcolor",
    ],
)
