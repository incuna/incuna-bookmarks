from os.path import dirname, join
from setuptools import find_packages, setup

def fread(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
    name='django-bookmarks',
    version=__import__('bookmarks').__version__,
    description='A reusable Django app for bookmark management.',
    long_description=fread('README'),
    author='James Tauber',
    author_email='jtauber@jtauber.com',
    url='http://github.com/incuna/django-bookmarks',
    packages=find_packages(),
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
