import setuptools
from setuptools import find_packages

setuptools.setup(
    name="GreParl",
    version="0.3",
    author="George Vasiliadis",
    author_email="geor.vasiliadis@gmail.com",
    description="Grep the Greek Parliament",
    long_description=open("README.md", "r", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GeorgeVasiliadis/GreParl",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": ["greparl=greparl.__main__:main"]
    },
    install_requires=[
        "flask",
        "numpy",
        "nltk",
        "scikit-learn",
        "scipy",
        "pyyaml"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: User Interfaces",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    zip_safe=False
)
