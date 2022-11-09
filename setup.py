# coding=utf-8
from setuptools import setup

setup(
    name='bandcamp-player',
    version='0.0.0',
    packages=['bandcamp_player', 'bandcamp_parser'],
    url='https://github.com/strizhechenko/bandcamp-player',
    license='MIT',
    author='helder opdebeeck',
    author_email='helderopdebeeck@gmail.com',
    description='Utility for streaming random music from bandcamp by specified genre/subgenre',
    classifiers=[
        'Development Status :: 0 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: Public Domain',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[

    ],
    entry_points={
        'console_scripts': [
            'bandcamp-player=bandcamp_player.__init__:main',
        ],
    },
)
