#!/usr/bin/env python3
"""
Setup script for X-Pull-Request-Reviewer
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="x-pull-request-reviewer",
    version="0.0.1",
    author="Inder Chauhan",
    author_email="inder@anzx.ai",
    description="Enterprise-Grade, Offline, LLM-Powered Code Review Agent",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/inderanz/x-pull-request-reviewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "xprr=xprr_agent:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md"],
    },
    keywords="code-review, pull-request, security, llm, ai, devops, devsecops",
    project_urls={
        "Bug Reports": "https://github.com/inderanz/x-pull-request-reviewer/issues",
        "Source": "https://github.com/inderanz/x-pull-request-reviewer",
        "Documentation": "https://github.com/inderanz/x-pull-request-reviewer/docs",
    },
) 