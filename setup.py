##############################################################################
#
# Copyright (c) 2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.0',
    'Jinja2>=2.5.0'
]

try:
    import wsgiref
except ImportError:
    requires.append('wsgiref')


setup(name='pyramid_jinja2',
      version='1.2',
      description='Jinja2 template bindings for the Pyramid web framework',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Framework :: Pylons",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi pylons pyramid',
      author="Rocky Burt",
      author_email="pylons-discuss@googlegroups.com",
      url="https://github.com/Pylons/pyramid_jinja2",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires + ['WebTest'],
      test_suite="pyramid_jinja2",
      entry_points="""
        [paste.paster_create_template]
        pyramid_jinja2_starter=pyramid_jinja2.paster:Jinja2ProjectTemplate
      """,
      )
