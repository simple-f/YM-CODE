#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取版本
def get_version():
    version_file = this_directory / "ymcode" / "__version__.py"
    if version_file.exists():
        exec(compile(version_file.read_text(), version_file, 'exec'))
        return locals().get('__version__', '0.1.0')
    return '0.1.0'

setup(
    name='ym-code',
    version=get_version(),
    description='YM-CODE - AI Programming Assistant',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='YM-CODE Team',
    author_email='team@ym-code.dev',
    url='https://github.com/ym-code/ym-code',
    license='MIT',
    
    # 包发现
    packages=find_packages(exclude=['tests', 'docs']),
    
    # Python 版本要求
    python_requires='>=3.10',
    
    # 依赖
    install_requires=[
        'rich>=13.0.0',
        'aiohttp>=3.9.0',
        'pydantic>=2.0.0',
        'click>=8.0.0',
        'pyyaml>=6.0.0',
        'httpx>=0.25.0',
    ],
    
    # 开发依赖
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'mkdocs>=1.5.0',
            'mkdocs-material>=9.0.0',
        ],
        'lsp': [
            'pygls>=1.0.0',
        ],
        'database': [
            'pymysql>=1.1.0',
            'psycopg2-binary>=2.9.0',
        ],
        'docker': [
            'docker>=6.0.0',
        ],
    },
    
    # 入口点
    entry_points={
        'console_scripts': [
            'ym-code=ymcode.cli.app:main',
        ],
    },
    
    # 包数据
    package_data={
        'ymcode': ['py.typed'],
    },
    
    # 分类
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    
    # 项目链接
    project_urls={
        'Documentation': 'https://ym-code.dev/docs',
        'Source': 'https://github.com/ym-code/ym-code',
        'Tracker': 'https://github.com/ym-code/ym-code/issues',
    },
)
