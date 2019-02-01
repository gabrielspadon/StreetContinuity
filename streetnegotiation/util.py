# coding=utf-8
#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


import osmnx as ox
import numpy as np


def compute_distance(source_coordinates: tuple, target_coordinates: tuple):
    """
    This method computes the double-precision floating-point straight-line distance between two nodes.
    :param source_coordinates: coordinates of the source note (longitude, latitude)
    :param target_coordinates: coordinates of the target node (longitude, latitude)
    :return: float
    """

    # extracting nodes coordinates
    source_longitude, source_latitude = source_coordinates
    target_longitude, target_latitude = target_coordinates

    # calculating the length of the edge
    return np.round(ox.great_circle_vec(source_latitude, source_longitude, target_latitude, target_longitude), 2)


def compute_angle(neighbor, source, target):
    """
    Computing the angle between (neighbor, source) and (source, target) using the law of cosines.
    The formula is given by cos(angle) = (a² + b² - c²) / (2ab), in which:
        [a] is the distance from neighbor to source;
        [b] is the distance from source to target; and,
        [c] is the distance from neighbor to target.
    :param neighbor: the first node of the triplet
    :param source: the intermediate node, also known as negotiator
    :param target: the last node of the triplet
    :return: float
    """

    # estimating the triangle's sides length
    d_sn = compute_distance(neighbor, source)
    d_nt = compute_distance(source, target)
    d_st = compute_distance(neighbor, target)

    # calculating the law of cosines and forcing bounds into -1 and +1
    cos_law = np.min(np.max(-1, (((d_sn ** 2) + (d_nt ** 2) - (d_st ** 2)) / (2 * d_sn * d_nt))), 1)

    # computing the angle in degrees
    return np.acos(cos_law) * (180 / np.pi)
