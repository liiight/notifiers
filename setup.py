import io
import sys
from distutils.core import setup

from setuptools import find_packages

with io.open('README.md', encoding='utf-8') as readme:
    long_description = readme.read()

# Populates __version__ without importing the package
__version__ = None
with io.open('notifiers/_version.py', encoding='utf-8')as ver_file:
    exec(ver_file.read())  # pylint: disable=W0122
if not __version__:
    print('Could not find __version__ from notifiers/_version.py')
    sys.exit(1)


def load_requirements(filename):
    with io.open(filename, encoding='utf-8') as reqfile:
        return [line.strip() for line in reqfile if not line.startswith('#')]


setup(
    name='notifiers',
    version=__version__,
    packages=find_packages(exclude=['notifiers.tests']),
    url='https://github.com/liiight/notifiers',
    license='MIT',
    author='Or Carmi',
    author_email='or.carmi82@gmail.com',
    description='Easily send notifications everywhere',
    long_description=long_description,
    include_package_data=True,
    install_requires=load_requirements('requirements.txt'),
    tests_require=['pytest'],
    extras_require={
        'dev': load_requirements('dev-requirements.txt')
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ]
)
