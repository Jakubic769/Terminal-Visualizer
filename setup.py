#!/usr/bin/env python3
"""Setup script for Terminal Visualizer.

This file serves as a fallback for older pip versions
and direct python setup.py install workflows.
The canonical build configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="visualizer-music",
    version="1.0.0",
    description="Cross-platform, per-application music visualizer (cava-style, but with more styles, colors and a now-playing bar).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Jakubic769",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(include=["visualizer*"]),
    include_package_data=True,
    install_requires=[
        "numpy>=1.24",
        "pygame>=2.5.0",
        'PyAudioWPatch>=0.2.12.7; sys_platform == "win32"',
        'pycaw>=20240210; sys_platform == "win32"',
        'winsdk>=1.0.0b10; sys_platform == "win32"',
        'comtypes>=1.2.0; sys_platform == "win32"',
    ],
    entry_points={
        "console_scripts": [
            "visualizer=visualizer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
    ],
)