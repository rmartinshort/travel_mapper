#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

this_verison = "1.1.0"

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# read from requirements file
requirements = [ ]

test_requirements = [ ]

setup(
    author="Robert Martin-Short",
    author_email='rmartinshort@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A travel agent that uses calls to OpenAI to build an itinerary and then Google Maps API to gather directions",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='travel_mapper',
    name='travel_mapper',
    packages=find_packages(include=['travel_mapper', 'travel_mapper.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rmartinshort/travel_mapper',
    version=this_verison,
    zip_safe=False,
)
