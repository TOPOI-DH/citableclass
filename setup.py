from setuptools import setup, find_packages

setup(
    # Application name:
    name="citableclass",

    # Version number (initial):
    version="0.0.10",

    # Application author details:
    author="Gordon Fischer",
    author_email="gordon.fischer@topoi.org",

    # Packages
    packages=["citableclass"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    #url="http://pypi.python.org/pypi/citableclass/",
    url="http://pypi.python.org/pypi/citableclass/",
    license="LICENSE.txt",
    description="Tool for data request",

    long_description=open("README.md").read(),

    classifiers=[
        # How mature is this project?
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3',
    ],
    project_urls={
        'Source': 'https://github.com/TOPOI-DH/citableclass/',
        'Tracker': 'https://github.com/TOPOI-DH/citableclass/issues',
    },

    download_url='https://github.com/TOPOI-DH/citableclass/archive/0.0.1.tar.gz',

    python_requires='>=3',

    # Dependent packages (distributions)
    install_requires=[
        "pandas", "matplotlib", "plyfile", "requests",  "IPython"
    ],
)
