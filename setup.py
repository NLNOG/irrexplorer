#!/usr/bin/env python
import setuptools
from irrd import __version__

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='irrexplorer',
    version=__version__,
    author='DashCare for Stichting NLNOG',
    author_email='irrexplorer@dashcare.nl',
    description='IRRexplorer',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/dashcare/irrexplorer',
    packages=setuptools.find_packages(
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests'],
    ),
    python_requires='>=3.7',
    package_data={'': ['*.txt', '*.yaml', '*.mako']},
    install_requires=[
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
)
