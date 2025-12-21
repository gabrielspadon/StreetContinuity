#
#   Copyright 2019-2024, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#

from pathlib import Path

from setuptools import setup

# Read README with safe fallback
this_directory = Path(__file__).parent
readme_file = this_directory / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name='StreetContinuity',
    version='0.1.0',
    description='StreetContinuity is a tool-set to maps primal graphs to dual graphs, focusing on street networks.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    keywords='street networks, dual graphs, primal graphs, urban analysis, GIS',
    platforms='any',
    url='https://github.com/gabrielspadon/StreetContinuity',
    author='Gabriel Spadon',
    author_email='gabriel@spadon.com.br',
    license='GPL-3.0',
    packages=['street_continuity'],
    python_requires='>=3.10,<3.13',
    install_requires=[
        'numpy>=1.24.0,<3.0',
        'osmnx>=2.0.0,<3.0',  # Pinned to 2.x to avoid API incompatibilities
        'networkx>=2.6.0,<4.0',
        'geopandas>=0.9.0,<1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'ruff>=0.1.0',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
