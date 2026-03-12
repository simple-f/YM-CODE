#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 安装脚本

使用方法：
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# 读取 requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()
requirements = [r.strip() for r in requirements if r.strip() and not r.startswith("#")]

setup(
    name="ym-code",
    version="0.2.0",
    author="YM-CODE Team",
    author_email="ym-code@example.com",
    description="YM-CODE - Next Generation AI Programming Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/simple-f/YM-CODE",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ym-code=ymcode.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ymcode": ["py.typed"],
    },
)
