from setuptools import find_packages, setup

# fake to satisfy mypy
__version__ = "0.0.0"
exec(open("ed_tutor/version.py").read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ed_tutor",
    version=__version__,
    description="",
    author="Sam Cox",
    author_email="swrig30@ur.rochester.edu",
    url="https://github.com/",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain_openai",
        "openai",
        "requests",
        "streamlit",
        ],
    test_suite="tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)