#!/bin/env python
# -*- coding: utf-8 -*-
"""
    setup

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: Modified BSD, see LICENSE for more details.
"""


from setuptools import setup

setup(
    name="tryton-bench",
    license="Modified BSD",
    version="0.1",
    decription="Tryton",
    author="Vishesh Yadav",
    author_email="vishesh.yadav@openlabs.co.in",
    install_requires=["requests"],
    scripts=["tryton_bench"],
    zip_safe=False
)
