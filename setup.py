from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


version = '0.1.4'


setup(
    name='hecho',
    version=version,
    description='Simple fast HTTP echo server',
    long_description=long_description,
    author='Pedro Buteri Gonring',
    author_email='pedro@bigode.net',
    url='https://github.com/pdrb/hecho',
    license='MIT',
    classifiers=[],
    keywords='fast http echo server',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['falcon', 'bjoern'],
    entry_points={
        'console_scripts': ['hecho=hecho.hecho:main'],
    },
)
