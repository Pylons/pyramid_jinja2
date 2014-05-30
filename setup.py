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
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
if sys.version_info[0] > 2:
    README = open(os.path.join(here, 'README.rst'), encoding="utf-8").read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt'), encoding="utf-8").read()
else:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.0.2', # wsgiref server entry point
    'zope.deprecation',
]

if (3,) < sys.version_info < (3, 3):
    requires.extend([
        'Jinja2>=2.5.0,<2.7dev', #2.7 drops Python 3.2 compat.
        'markupsafe<0.16', #0.16 drops Python 3.2 compat
        ])
else:
    requires.extend([
        'Jinja2>=2.5.0',
        'markupsafe',
        ])

try:
    import wsgiref
except ImportError:
    requires.append('wsgiref')

testing_extras = ['WebTest', 'nose>=1.2.0', 'coverage']
docs_extras = ['Sphinx']

setup(name='pyramid_jinja2',
      version='2.2',
      description='Jinja2 template bindings for the Pyramid web framework',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi pylons pyramid',
      author="Rocky Burt",
      author_email="pylons-discuss@googlegroups.com",
      maintainer="Domen Kozar",
      maintainer_email="domen@dev.si",
      url="https://github.com/Pylons/pyramid_jinja2",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require = {
          'testing':testing_extras,
          'docs':docs_extras,
          },
      tests_require=requires + ['WebTest'],
      test_suite="pyramid_jinja2.tests",
      entry_points="""
        [paste.paster_create_template]
        pyramid_jinja2_starter=pyramid_jinja2.scaffolds:Jinja2ProjectTemplate
        [pyramid.scaffold]
        pyramid_jinja2_starter=pyramid_jinja2.scaffolds:Jinja2ProjectTemplate
      """,
      )
