"""Unit tests for the geometry helpers in ``street_continuity.util``."""

import numpy as np
import pytest

from street_continuity.util import compute_angle, compute_distance


class TestComputeDistance:
    """The distance helper treats coordinates as (latitude, longitude)."""

    def test_passes_lat_lon_in_order(self, monkeypatch):
        captured = {}

        def fake_great_circle(lat1, lon1, lat2, lon2):
            captured["args"] = (lat1, lon1, lat2, lon2)
            return 100.456

        monkeypatch.setattr("street_continuity.util.oxd.great_circle", fake_great_circle)

        source = (10.0, 20.0)  # (latitude, longitude)
        target = (10.5, 20.5)
        result = compute_distance(source, target)

        assert captured["args"] == (10.0, 20.0, 10.5, 20.5)
        assert result == 100.46  # rounded to two decimals

    def test_zero_distance_for_identical_points(self, monkeypatch):
        monkeypatch.setattr("street_continuity.util.oxd.great_circle", lambda *_: 0.0)
        coords = (45.0, 90.0)
        assert compute_distance(coords, coords) == 0.0

    def test_rounds_to_two_decimals(self, monkeypatch):
        monkeypatch.setattr("street_continuity.util.oxd.great_circle", lambda *_: 123.456789)
        assert compute_distance((0, 0), (1, 1)) == 123.46

    def test_real_great_circle_matches_reference(self):
        # Two nodes from the shipped sample network (Ji-Parana, Brazil).
        n0 = (-11.9227393, -62.0014909)  # (lat, lon)
        n2 = (-11.9235226, -62.0014710)
        # The edge list ships the precomputed length for this pair.
        assert compute_distance(n0, n2) == pytest.approx(87.13, abs=1.0)


class TestComputeAngle:
    """The angle helper applies the law of cosines to three node coordinates."""

    def test_right_angle(self, monkeypatch):
        sides = iter([3.0, 4.0, 5.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        assert compute_angle((0, 0), (3, 0), (3, 4)) == pytest.approx(90.0, abs=0.01)

    def test_straight_line(self, monkeypatch):
        sides = iter([5.0, 5.0, 10.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        assert compute_angle((0, 0), (5, 0), (10, 0)) == pytest.approx(180.0, abs=0.01)

    def test_equilateral_is_sixty_degrees(self, monkeypatch):
        sides = iter([5.0, 5.0, 5.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        assert compute_angle((0, 0), (5, 0), (2.5, 4.33)) == pytest.approx(60.0, abs=1.0)

    def test_obtuse_angle(self, monkeypatch):
        sides = iter([3.0, 4.0, 6.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        assert compute_angle((0, 0), (3, 0), (0, 4)) > 90.0

    def test_clamped_when_triangle_impossible(self, monkeypatch):
        sides = iter([1.0, 1.0, 3.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        angle = compute_angle((0, 0), (1, 0), (2, 0))
        assert 0.0 <= angle <= 180.0

    def test_zero_length_segment_returns_zero(self, monkeypatch):
        sides = iter([0.0, 5.0, 5.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        assert compute_angle((0, 0), (0, 0), (5, 0)) == 0.0

    def test_result_is_scalar_in_degrees(self, monkeypatch):
        sides = iter([3.0, 4.0, 5.0])
        monkeypatch.setattr("street_continuity.util.compute_distance", lambda *_: next(sides))
        angle = compute_angle((0, 0), (3, 0), (3, 4))
        assert isinstance(angle, (int, float, np.number))
        assert 0.0 <= angle <= 180.0
