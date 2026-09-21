# -*- coding: utf-8 -*-
"""
Created on 2020/4/22 10:45 PM
---------
@summary:
---------
@author: wangwei
@email: ww_geophy@126.com
"""

from os.path import dirname, join
from sys import version_info

import setuptools

if version_info < (3, 0, 0):
    raise SystemExit("Sorry! jmcode requires python 3.0.0 or later.")

with open(join(dirname(__file__), "VERSION"), "rb") as f:
    version = f.read().decode("ascii").strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

packages = setuptools.find_packages()
cython_version = "Cython==3.3.0" if version_info >= (3, 11) else "Cython==0.29.20"
# Python 3.6-3.10 uses the generic py3 wheel tag; Python 3.11+ uses py311.
python_tag = "py311" if version_info >= (3, 11) else "py3"

setuptools.setup(
    name="jmcode",
    version=version,
    author="wangwei",
    license="MIT",
    author_email="ww_geophy@126.com",
    description="python项目代码一键加密打包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[cython_version, "PyYAML>=6.0"],
    entry_points={
        "console_scripts": [
            "jmpy = jmcode.cmdline:execute",
            "cpsrc = jmcode.cmdline_cpsrc:execute",
            "jmcode = jmcode.cmdline_jmpro:execute",
        ]
    },
    url="https://github.com/wangweiwei104/jmcode",
    packages=packages,
    include_package_data=True,
    python_requires=">=3.0",
    options={"bdist_wheel": {"python_tag": python_tag, "plat_name": "any"}},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
