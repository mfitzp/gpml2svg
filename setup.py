#!/usr/bin/env python
# coding=utf-8

import sys
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

version_string = '0.1.2'


# Defaults for py2app / cx_Freeze
default_build_options=dict(
    packages=['wheezy.template'],
    )


setup(

    name='gpml2svg',
    version=version_string,
    author='Martin Fitzpatrick',
    author_email='martin.fitzpatrick@gmail.com',
    url='https://github.com/mfitzp/gpml2svg',
    download_url='https://github.com/mfitzp/gpml2svg/zipball/master',
    description='Render GPML pathway markup to SVG from the commandline/Python.',
    long_description='GPML2SVG is a command line and Python API for the conversion of pathways marked up \
        using GPML to SVG. The command-line interface is currently basic. Simply call the script with the name of the \
        GPML file to convert. The resulting SVG will be saved using the same name, with the \
        extension change to .svg. The resulting SVG is marked up with object identifiers, \
        and links to relevant databases. The python interface offers a single function call to which you can optionally provide \
        colouring information (for data visualisation) and links for custom XRefs. \
        The sofware is in development as an extension to MetaPath.',
    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '': ['*.txt', '*.rst', '*.md'],
        'gpml2svg':['*.svg'],
    },
    exclude_package_data = { '': ['README.txt'] },

    entry_points = {
        'console_scripts': [
            'gpml2svg = gpml2svg.gpml2svg:main',
        ],
    },

    install_requires = ['wheezy.template>=0.1.135'],

    keywords='bioinformatics metabolomics signalling pathways research analysis science',
    license='GPL',
    classifiers=['Development Status :: 4 - Beta',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               'Topic :: Education',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Education',
              ],
    )