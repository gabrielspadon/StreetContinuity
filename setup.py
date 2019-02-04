"""
StreetContinuity (SC)
========
    StreetContinuity (SC) is a python library that implements both Intersection Continuity Negotiation (ICN) and
    Hierarchical Intersection Continuity Negotiation (HICN). ICN was first proposed by Porta et al. (2006) and
    further enhanced by Masucci et al. (2014), who advanced with the HICN approach.

    For details about each implementation, please refer to:

    [1] Sergio Porta, Paolo Crucitti, Vito Latora, "The network analysis of urban streets: A dual approach", Physica A:
        Statistical Mechanics and its Applications, Volume 369, Issue 2, 2006, Pages 853-866, ISSN 0378-4371.

    [2] Masucci, A. P., Stanilov, K., Batty, M. (2014). "Exploring the evolution of London's street
        network in the information space: A dual approach." Physical Review E, 89(1), 012805.

    I want to thank Elisabeth H. Krueger and Xianyuan Zhan, who provide me with their version of the HICN.
    Their code gave some insights and helped in the process of validation of the results.

    For details about their implementation, please refer to:

    [3] Krueger, E., Klinkhamer, C., Urich, C., Zhan, X., & Rao, P. S. C. (2017). "Generic patterns in the evolution
        of urban water networks: Evidence from a large Asian city". Physical Review E, 95(3), 032312.

    Portfolio::
        https://spadon.com.br/

    Source::
        https://github.com/gabrielspadon/StreetContinuity

    Bug reports::
        https://github.com/gabrielspadon/StreetContinuity/issues

Simple example
--------------

    >>> from street_continuity.all import *

    >>> import osmnx as ox

    >>> oxg = ox.graph_from_point((-22.012282, -47.890821), distance=5000)

    >>> p_graph = from_osmnx(oxg=oxg, use_label=True)
    >>> d_graph = dual_mapper(primal_graph=p_graph, min_angle=120)

    >>> write_graphml(graph=d_graph, filename='file.graphml', directory='../data')
    >>> write_supplementary(graph=d_graph, filename='supplementary.txt', directory='../data')

Bugs
----
    Please report any bugs that you find `here <https://github.com/gabrielspadon/StreetContinuity/issues>`.
    Or, even better, fork the repository on GitHub and create a pull request.

License
-------
    Released under the GNU General Public License v3.0 (GLP-3.0).
    Copyright 2019, Gabriel Spadon, all rights reserved.
        www.spadon.com.br & gabriel@spadon.com.br
"""

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='StreetContinuity',
      version='0.1',
      description='StreetContinuity is a tool-set to map primal graphs to dual graphs focused on street networks.',
      classifiers=[
        'Development Status :: 0 - Alpha',
        'License :: GNU General Public License v3.0',
        'Programming Language :: Python :: 3.6',
        'Topic :: Graph Processing',
      ],
      keywords='primal graph, primal network, dual graph, dual network',
      url='https://github.com/gabrielspadon/StreetContinuity',
      author='Gabriel Spadon',
      author_email='gabriel@spadon.com.br',
      license='GLP-3.0',
      packages=['street_continuity'],
      install_requires=[
          'numpy',
          'osmnx',
          'networkx',
      ],
      include_package_data=True,
      zip_safe=False)
