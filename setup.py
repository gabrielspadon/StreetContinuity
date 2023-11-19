#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 4th, 2019.

from setuptools import setup

setup(name='StreetContinuity',
      version='0.1',
      description='StreetContinuity is a tool-set to maps primal graphs to dual graphs, focusing on street networks.',
      classifiers=[
        'Development Status :: 0 - Alpha',
        'License :: GNU General Public License v3.0',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
        'Topic :: Graph Processing',
      ],
      platforms='any',
      url='https://github.com/gabrielspadon/StreetContinuity',
      author='Gabriel Spadon',
      author_email='gabriel@spadon.com.br',
      license='GLP-3.0',
      packages=['street_continuity'],
      install_requires=[
          'numpy>=1.26.2',
          'osmnx>=1.7.1',
          'networkx>=3.2.1',
      ],
      include_package_data=True,
      zip_safe=False)
