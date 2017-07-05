from setuptools import setup
from os import path

directory = path.abspath(path.dirname(__file__))
readme_path = path.join(directory, 'README.md')

try:
    import pypandoc
    long_description = pypandoc.convert(readme_path, 'rst')
except (IOError, ImportError):
    long_description = open(readme_path, encoding='utf-8').read()

setup(
    name='beets-popularity',
    version='1.0.2',
    description="""Beets plugin to fetch and store popularity values as
        flexible item attributes""",
    long_description=long_description,
    url='https://github.com/abba23/beets-popularity',
    download_url='https://github.com/abba23/beets-popularity.git',
    author='abba23',
    author_email='628208@gmail.com',
    license='MIT',
    platforms='ALL',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Sound/Audio',
        'Environment :: Console',
    ],
    packages=['beetsplug'],
    namespace_packages=['beetsplug'],
    install_requires=['beets>=1.4.3', 'requests>=2.13.0'],
)
