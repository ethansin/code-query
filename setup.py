from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, "r") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]


setup(
    name="code-query",
    version="0.1.0",
    author="Ethan Sin",
    author_email="etansincos@gmail.com",
    description="A tool for querying about a codebase",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ethansin/code-query",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
