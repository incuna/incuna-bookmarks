from setuptools import find_packages, setup
from os.path import dirname, join

from bookmarks import get_version

def fread(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
    name='incuna-bookmarks',
    version=get_version(),
    description='A reusable Django app for bookmark management.',
    long_description=fread('README'),
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='http://github.com/incuna/incuna-bookmarks',
    packages=find_packages(),
    include_package_data=True,
    package_dir={'bookmarks': 'bookmarks'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
