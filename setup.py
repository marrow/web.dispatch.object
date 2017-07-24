#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import os
import sys
import codecs

from setuptools import setup


if sys.version_info < (3, 3):
	raise SystemExit("Python 3.3 or later is required.")

version = description = url = author = None

exec(open(os.path.join("web", "dispatch", "object", "release.py")).read())


here = os.path.abspath(os.path.dirname(__file__))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-catchlog',  # log capture
		'pytest-isort',  # import ordering
	]


setup(
	name = "web.dispatch.object",
	version = version,
	
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	download_url = 'https://pypi.org/project/web.dispatch.object/',
	
	author = author.name,
	author_email = author.email,
	
	license = 'MIT',
	keywords = ['marrow', 'dispatch', 'object dispatch', 'endpoint discovery'],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Environment :: Console",
			"Environment :: Web Environment",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	packages = ['web.dispatch.object'],
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	zip_safe = False,
	
	# Dependency Declaration
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	
	install_requires = [
			'web.dispatch~=3.0.1',  # Core dispatch helpers.
			'pathlib; python_version < "3.4"',  # Path manipulation utility lib; builtin in 3.4 and 3.5.
		],
	
	extras_require = dict(
			development = tests_require + ['pre-commit'],  # Development-time dependencies.
		),
	
	tests_require = tests_require,
	
	# Plugin Registration
	
	entry_points = {
			'web.dispatch': [
					'object = web.dispatch.object:ObjectDispatch',
				],
		},
)
