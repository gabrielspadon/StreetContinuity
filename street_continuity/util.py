#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


import numpy as np
import osmnx.distance as oxd


def compute_distance(source_coordinates: tuple, target_coordinates: tuple) -> float:
    """
    Compute the great-circle distance between two geographic coordinates.

    Uses the haversine formula to calculate the shortest distance between two points
    on the Earth's surface, given their latitude and longitude. This assumes Earth
    is a perfect sphere.

    Args:
        source_coordinates: Tuple of (latitude, longitude) for source point in decimal degrees
        target_coordinates: Tuple of (latitude, longitude) for target point in decimal degrees

    Returns:
        float: Distance in meters, rounded to 2 decimal places

    Example:
        >>> # Distance from New York to Los Angeles (approximately)
        >>> nyc = (40.7128, -74.0060)  # (lat, lon)
        >>> la = (34.0522, -118.2437)
        >>> distance = compute_distance(nyc, la)
        >>> print(f"{distance / 1000:.0f} km")
        3936 km

    Note:
        This function uses the great_circle formula which is accurate for most
        purposes but assumes a spherical Earth. For sub-meter accuracy, consider
        using geodesic calculations.
    """

    # extracting node coordinates (internal representation is latitude, longitude)
    source_latitude, source_longitude = source_coordinates
    target_latitude, target_longitude = target_coordinates

    # calculating the length of the edge
    return np.round(
        oxd.great_circle(source_latitude, source_longitude, target_latitude, target_longitude),
        2,
    )


def compute_angle(neighbor, source, target) -> float:
    """
    Compute the continuity angle at an intersection using the law of cosines.

    Calculates the interior (convex) angle between two street segments meeting at an
    intersection. This is the quantity ICN/HICN threshold with ``min_angle``; a street
    continues through the intersection when this angle is large enough. An angle of
    180 degrees means the two segments are perfectly collinear, while 0 degrees means
    a full U-turn, so the deflection from straight ahead is 180 minus this value.

    The angle follows the law of cosines, cos(theta) = (a^2 + b^2 - c^2) / (2ab),
    with a the neighbor-to-source distance, b the source-to-target distance, and
    c the neighbor-to-target distance.

    Args:
        neighbor: Coordinates (lat, lon) of the first node in the triplet
        source: Coordinates (lat, lon) of the intersection node (negotiator)
        target: Coordinates (lat, lon) of the third node in the triplet

    Returns:
        float: Angle in degrees (0-180), where 180 indicates a straight line
            and 0 indicates a sharp U-turn

    Example:
        >>> # Right angle intersection
        >>> neighbor = (0.0, 0.0)
        >>> source = (0.0, 1.0)
        >>> target = (1.0, 1.0)
        >>> angle = compute_angle(neighbor, source, target)
        >>> print(f"{angle:.1f} degrees")
        90.0 degrees

    Note:
        Overlapping nodes (a zero-length side) return 0.0, and the cosine is clamped
        to [-1, 1] so floating-point imprecision cannot push arccos out of domain.
    """
    # estimating the triangle's sides length
    d_sn = compute_distance(neighbor, source)
    d_nt = compute_distance(source, target)
    d_st = compute_distance(neighbor, target)

    # Guard against division by zero when nodes overlap
    if d_sn * d_nt == 0:
        return 0.0

    # calculating the law of cosines and forcing bounds into -1 and +1
    cos_law = min(
        max(-1.0, (((d_sn**2.0) + (d_nt**2.0) - (d_st**2.0)) / (2.0 * d_sn * d_nt))),
        1.0,
    )

    # computing the angle in degrees
    return float(np.arccos(cos_law) * (180.0 / np.pi))
