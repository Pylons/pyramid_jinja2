##############################################################################
#
# Copyright (c) 2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# https://pylonsproject.org/license.html. A copy of the license should
# accompany this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND
# ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT,
# AND FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

from setuptools import find_packages, setup

README = open("README.rst").read()
CHANGES = open("CHANGES.txt").read()

requires = [
    "Jinja2>=2.5.0,!=2.11.0,!=2.11.1",
    "MarkupSafe",
    "pyramid>=1.3.0",  # pyramid.path.DottedNameResolver
    "zope.deprecation",
]

testing_extras = [
    "coverage",
    "nose>=1.2.0",
    "WebTest",
]
docs_extras = [
    "pylons-sphinx-themes >= 0.3",
    "Sphinx>=1.7.5",
]

setup(
    name="pyramid_jinja2",
    version="2.8",
    description="Jinja2 template bindings for the Pyramid web framework",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Pyramid",
        "License :: Repoze Public License",
    ],
    keywords="web wsgi pylons pyramid jinja2",
    author="Rocky Burt",
    author_email="pylons-discuss@googlegroups.com",
    maintainer="Domen Kozar",
    maintainer_email="domen@dev.si",
    url="https://github.com/Pylons/pyramid_jinja2",
    license="BSD-derived (https://pylonsproject.org/license.html)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={"testing": testing_extras, "docs": docs_extras,},
    tests_require=requires + ["WebTest"],
    test_suite="pyramid_jinja2.tests",
    python_requires=">=3.6",
    entry_points="""
        [pyramid.scaffold]
        pyramid_jinja2_starter=pyramid_jinja2.scaffolds:Jinja2ProjectTemplate
      """,
)
