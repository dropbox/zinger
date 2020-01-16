from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="zinger",
    version="1.1.0",
    description="zinger is a Python script for interacting with the Zingtree API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="dtf",
    licence="Apache-2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Customer Service",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    keywords="zingtree",
    packages=find_packages(),
    install_requires=["requests", "python-dotenv", "pathlib"],
    python_requires="~=3.5"
)