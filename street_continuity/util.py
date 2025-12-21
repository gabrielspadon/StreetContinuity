#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


import numpy as np

# Import distance module (compatible with OSMnx 1.x and 2.x)
try:
    # OSMnx 2.0+ uses ox.distance module
    import osmnx.distance as oxd
except ImportError:
    # OSMnx 1.x also uses ox.distance, but just in case
    import osmnx as ox
    oxd = ox.distance


def compute_distance(source_coordinates: tuple, target_coordinates: tuple) -> float:
    """
    Compute the great-circle distance between two geographic coordinates.

    Uses the haversine formula to calculate the shortest distance between two points
    on the Earth's surface, given their longitude and latitude. This assumes Earth
    is a perfect sphere.

    Args:
        source_coordinates: Tuple of (longitude, latitude) for source point in decimal degrees
        target_coordinates: Tuple of (longitude, latitude) for target point in decimal degrees

    Returns:
        float: Distance in meters, rounded to 2 decimal places

    Example:
        >>> # Distance from New York to Los Angeles (approximately)
        >>> nyc = (-74.0060, 40.7128)  # (lon, lat)
        >>> la = (-118.2437, 34.0522)
        >>> distance = compute_distance(nyc, la)
        >>> print(f"{distance / 1000:.0f} km")
        3936 km

    Note:
        This function uses the great_circle formula which is accurate for most
        purposes but assumes a spherical Earth. For sub-meter accuracy, consider
        using geodesic calculations.
    """

    # extracting nodes coordinates
    source_longitude, source_latitude = source_coordinates
    target_longitude, target_latitude = target_coordinates

    # calculating the length of the edge
    return np.round(oxd.great_circle(source_latitude, source_longitude, target_latitude, target_longitude), 2)


def compute_angle(neighbor, source, target) -> float:
    """
    Compute the deflection angle at an intersection using the law of cosines.

    Calculates the angle between two street segments meeting at an intersection.
    This is used in street continuity analysis to determine which streets form
    the most "natural" continuation through an intersection.

    The law of cosines formula used is: cos(θ) = (a² + b² - c²) / (2ab), where:
        - a is the distance from neighbor to source
        - b is the distance from source to target
        - c is the distance from neighbor to target

    Args:
        neighbor: Coordinates (lon, lat) of the first node in the triplet
        source: Coordinates (lon, lat) of the intersection node (negotiator)
        target: Coordinates (lon, lat) of the third node in the triplet

    Returns:
        float: Angle in degrees (0-180), where 180° indicates a straight line
            and 0° indicates a sharp U-turn

    Example:
        >>> # Right angle intersection
        >>> neighbor = (0.0, 0.0)
        >>> source = (0.0, 1.0)
        >>> target = (1.0, 1.0)
        >>> angle = compute_angle(neighbor, source, target)
        >>> print(f"{angle:.1f}°")
        90.0°

    Note:
        The result is clamped to valid range to handle floating-point
        imprecision. Invalid values (like NaN from division by zero when
        nodes overlap) are suppressed.
    """
    # estimating the triangle's sides length
    d_sn = compute_distance(neighbor, source)
    d_nt = compute_distance(source, target)
    d_st = compute_distance(neighbor, target)

    # Guard against division by zero when nodes overlap
    if d_sn * d_nt == 0:
        return 0.0

    # calculating the law of cosines and forcing bounds into -1 and +1
    cos_law = min(max(-1.0, (((d_sn ** 2.0) + (d_nt ** 2.0) - (d_st ** 2.0)) / (2.0 * d_sn * d_nt))), 1.0)

    # computing the angle in degrees
    # Suppress invalid value warnings for arccos when input is at boundary [-1, 1]
    # This is expected behavior as we clamp cos_law to valid domain
    with np.errstate(invalid='ignore'):
        angle = np.arccos(cos_law) * (180.0 / np.pi)

    return angle
