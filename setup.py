# -*- coding: utf-8 -*-
"""Installer for the urban.dataimport.core package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='urban.dataimport.core',
    version='1.0',
    description="import script for urban import",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
    keywords='Urban script import',
    author='Julien Jaumotte',
    author_email='julien.jaumotte@imio.be',
    url='https://github.com/IMIO/urban.dataimport.core',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['urban', 'urban.dataimport'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pandas',
        'SQLAlchemy',
        'mysqlclient',
        'psycopg2',
        'jsonschema',
        'strict-rfc3339',
        'polib',
        'progress',
        'requests',
        'Unidecode',
    ],
    extras_require={
        'test': [
        ],
    },
    entry_points={
        'console_scripts': [
            'acropole_script = urban.dataimport.core.script.acropole:main',
            'urbaweb_script = urban.dataimport.core.script.urbaweb:main',
            'consolidate_script = urban.dataimport.core.script.consolidate:main',
            'import_to_plone_script = urban.dataimport.core.script.import_to_plone:main',
        ],
    },
)
