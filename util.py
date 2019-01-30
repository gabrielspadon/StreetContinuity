#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#

import osmnx as ox
import numpy as np


# helper function, compute the unit direction vector
def calculate_distance(source_coordinates, target_coordinates):
    # extracting nodes coordinates
    src_lon, src_lat = source_coordinates
    tgt_lon, tgt_lat = target_coordinates
    # calculating the double-precision floating-point length of the edge
    return np.round(ox.great_circle_vec(src_lat, src_lon, tgt_lat, tgt_lon), 2)


def compute_angle(neighbor, source, target):
    # estimating the triangle's sides length
    d_sn = calculate_distance(neighbor, source)
    d_nt = calculate_distance(source, target)
    d_st = calculate_distance(neighbor, target)

    # calculating the law of cosines: cos(angle) = (a² + b² - c²) / (2ab)
    cos_law = min(max(-1, (((d_sn ** 2) + (d_nt ** 2) - (d_st ** 2)) / (2 * d_sn * d_nt))), 1)
    return np.acos(cos_law) * (180 / np.pi)