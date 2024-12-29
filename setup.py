from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-repo-structure",
    version="0.1.0",
    packages=find_packages(where="github-repo-structure"),
    package_dir={"": "github-repo-structure"},
    install_requires=[
        "GitPython>=3.1.0",
        "pathspec>=0.9.0",
        "alive-progress>=3.1.0",
    ],
    author="Oguzhan Cetinkaya", 
    author_email="oguzhan.cetinkaya@gmail.com",
    description="A Python utility for analyzing GitHub repository structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oguzhancetinkaya/github-repo-structure",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",
)