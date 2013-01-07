#!/usr/bin/env python
"""
Flask-MenuBuilder
-----------

An easy way to create menus to use with flask.

"""

from setuptools import setup

def run_tests():
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
    from test_menubuilder import suite
    return suite()

setup(
    name='Flask-MenuBuilder',
    version='0.9.2',
    url='http://dev.ufsoft.org/projects/menu-builder',
    license='BSD',
    author='Pedro Algarvio',
    author_email='pedro@algarvio.me',
    description='An easy way to create menus to use with flask.',
    long_description=__doc__,
    py_modules=['flask_menubuilder'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='__main__.run_tests'
)
