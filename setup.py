#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import sys


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


version = "1.0.0"

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

setup(
    name='rapid_cloud',
    version=version,
    url='http://github.com/kkuuba/RapidCloud/',
    license='BSD',
    description='Commandline tool for exporting files to cloud storage',
    long_description_content_type='text/markdown',
    author='Jakub Kupiec',
    author_email='jakub.kupiec.k1@gmail.com',
    packages=get_packages('rapid_cloud'),
    package_data=get_package_data('rapid_cloud'),
    install_requires=["setuptools",
                      "PyDrive",
                      "pyAesCrypt",
                      "mega.py",
                      "file_split_merge"],
    entry_points={
        'console_scripts': ['rapid_cloud='
                            'rapid_cloud:main'],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
