from pathlib import Path

from setuptools import find_packages, setup

long_description = Path('README.MD').read_text()


def load_requirements(filename):
    with Path(filename).open() as reqfile:
        return [line.strip() for line in reqfile if not line.startswith('#')]


# Populates __version__ without importing the package
__version__ = None
with open('notifiers/_version.py', encoding='utf-8') as ver_file:
    exec(ver_file.read())  # pylint: disable=W0122

if not __version__:
    print('Could not find __version__ from notifiers/_version.py')
    exit(1)

setup(
    name='notifiers',
    version=__version__,
    packages=find_packages(exclude=['notifiers.tests']),
    url='https://github.com/notifiers/notifiers',
    license='MIT',
    author='Or Carmi',
    author_email='or.carmi82@gmail.com',
    description='The easy way to send notifications',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=load_requirements('requirements.txt'),
    tests_require=['pytest'],
    extras_require={
        'dev': load_requirements('dev-requirements.txt')
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop"
    ],
    entry_points="""
        [console_scripts]
        notifiers=notifiers_cli.core:entry_point
    """,
    python_requires='>=3.6'
)
