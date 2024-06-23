# coding=utf-8
#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


import warnings
import osmnx as ox
import numpy as np
import osmnx.distance as oxd


def compute_distance(source_coordinates: tuple, target_coordinates: tuple):
    """
    This method computes the double-precision floating-point straight-line distance between two nodes.
    :param source_coordinates: coordinates of the source node (longitude, latitude)
    :param target_coordinates: coordinates of the target node (longitude, latitude)
    :return: float
    """

    # extracting nodes coordinates
    source_longitude, source_latitude = source_coordinates
    target_longitude, target_latitude = target_coordinates

    # calculating the length of the edge
    return np.round(oxd.great_circle(source_latitude, source_longitude, target_latitude, target_longitude), 2)


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
    # avoiding unnecessary warning outputs
    warnings.filterwarnings('ignore')

    # estimating the triangle's sides length
    d_sn = compute_distance(neighbor, source)
    d_nt = compute_distance(source, target)
    d_st = compute_distance(neighbor, target)

    # calculating the law of cosines and forcing bounds into -1 and +1
    cos_law = min(max(-1.0, (((d_sn ** 2.0) + (d_nt ** 2.0) - (d_st ** 2.0)) / (2.0 * d_sn * d_nt))), 1.0)

    # computing the angle in degrees
    return np.arccos(cos_law) * (180.0 / np.pi)
