import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock osmnx before importing
sys.modules['osmnx'] = Mock()
sys.modules['osmnx.distance'] = Mock()

from street_continuity.util import compute_distance, compute_angle


class TestComputeDistance:
    """Test suite for compute_distance function."""

    @patch('street_continuity.util.oxd.great_circle')
    def test_compute_distance_basic(self, mock_great_circle):
        """Test basic distance computation."""
        mock_great_circle.return_value = 100.456

        source = (10.0, 20.0)  # (longitude, latitude)
        target = (10.5, 20.5)

        result = compute_distance(source, target)

        # Function should call great_circle with lat, lon order
        mock_great_circle.assert_called_once_with(20.0, 10.0, 20.5, 10.5)
        assert result == 100.46  # rounded to 2 decimals

    @patch('street_continuity.util.oxd.great_circle')
    def test_compute_distance_same_coordinates(self, mock_great_circle):
        """Test distance between same coordinates."""
        mock_great_circle.return_value = 0.0

        coords = (45.0, 90.0)
        result = compute_distance(coords, coords)

        assert result == 0.0

    @patch('street_continuity.util.oxd.great_circle')
    def test_compute_distance_rounding(self, mock_great_circle):
        """Test that distance is rounded to 2 decimal places."""
        mock_great_circle.return_value = 123.456789

        result = compute_distance((0, 0), (1, 1))

        assert result == 123.46

    @patch('street_continuity.util.oxd.great_circle')
    def test_compute_distance_parameter_order(self, mock_great_circle):
        """Test that parameters are passed in correct order (lat, lon)."""
        mock_great_circle.return_value = 50.0

        lon1, lat1 = 10.0, 20.0
        source = (lon1, lat1)
        lon2, lat2 = 30.0, 40.0
        target = (lon2, lat2)

        compute_distance(source, target)

        # Verify lat, lon order for both source and target
        mock_great_circle.assert_called_once_with(lat1, lon1, lat2, lon2)


class TestComputeAngle:
    """Test suite for compute_angle function."""

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_right_angle(self, mock_distance):
        """Test computing a 90-degree angle."""
        # Set up a right triangle with sides 3, 4, 5
        mock_distance.side_effect = [3.0, 4.0, 5.0]

        neighbor = (0, 0)
        source = (3, 0)
        target = (3, 4)

        angle = compute_angle(neighbor, source, target)

        # Should be 90 degrees
        assert abs(angle - 90.0) < 0.01

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_straight_line(self, mock_distance):
        """Test computing angle for collinear points (180 degrees)."""
        # For straight line: a + b = c
        mock_distance.side_effect = [5.0, 5.0, 10.0]

        angle = compute_angle((0, 0), (5, 0), (10, 0))

        # Should be approximately 180 degrees
        assert abs(angle - 180.0) < 0.01

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_acute(self, mock_distance):
        """Test computing an acute angle (< 90 degrees)."""
        # Equilateral triangle has 60-degree angles
        mock_distance.side_effect = [5.0, 5.0, 5.0]

        angle = compute_angle((0, 0), (5, 0), (2.5, 4.33))

        # Should be approximately 60 degrees
        assert abs(angle - 60.0) < 1.0

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_obtuse(self, mock_distance):
        """Test computing an obtuse angle (> 90 degrees)."""
        # Set up triangle with obtuse angle
        mock_distance.side_effect = [3.0, 4.0, 6.0]

        angle = compute_angle((0, 0), (3, 0), (0, 4))

        # Should be obtuse (> 90)
        assert angle > 90.0

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_boundary_cosine(self, mock_distance):
        """Test angle computation at cosine boundary values."""
        # Test with cos = 1 (0 degrees)
        mock_distance.side_effect = [5.0, 5.0, 0.0]

        angle = compute_angle((0, 0), (5, 0), (10, 0))

        # Result should be valid (0 or close to it)
        assert 0 <= angle <= 180

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_clamping(self, mock_distance):
        """Test that cosine law result is clamped to [-1, 1]."""
        # Force a calculation that might exceed bounds
        mock_distance.side_effect = [1.0, 1.0, 3.0]

        # Should not raise error even with impossible triangle
        angle = compute_angle((0, 0), (1, 0), (2, 0))

        # Should return valid angle in [0, 180]
        assert 0 <= angle <= 180

    @patch('street_continuity.util.compute_distance')
    def test_compute_angle_zero_distance(self, mock_distance):
        """Test angle computation with zero distances."""
        mock_distance.side_effect = [0.0, 5.0, 5.0]

        # This creates a degenerate triangle
        # Function should handle this gracefully
        try:
            angle = compute_angle((0, 0), (0, 0), (5, 0))
            # If no error, angle should be in valid range
            assert 0 <= angle <= 180 or np.isnan(angle)
        except (ZeroDivisionError, ValueError):
            # Also acceptable to raise an error
            pass


class TestUtilModule:
    """Test suite for utility module structure."""

    def test_module_imports(self):
        """Test that module can be imported."""
        import street_continuity.util as util
        assert hasattr(util, 'compute_distance')
        assert hasattr(util, 'compute_angle')

    def test_functions_callable(self):
        """Test that utility functions are callable."""
        import street_continuity.util as util
        assert callable(util.compute_distance)
        assert callable(util.compute_angle)

    def test_function_signatures(self):
        """Test that functions have correct signatures."""
        import inspect

        # compute_distance should take 2 parameters
        sig_dist = inspect.signature(compute_distance)
        assert len(sig_dist.parameters) == 2

        # compute_angle should take 3 parameters
        sig_angle = inspect.signature(compute_angle)
        assert len(sig_angle.parameters) == 3


class TestNumpyIntegration:
    """Test numpy integration in util functions."""

    @patch('street_continuity.util.compute_distance')
    def test_numpy_arccos_usage(self, mock_distance):
        """Test that numpy arccos is used correctly."""
        # Valid triangle
        mock_distance.side_effect = [3.0, 4.0, 5.0]

        angle = compute_angle((0, 0), (3, 0), (3, 4))

        # Result should be a number (not array)
        assert isinstance(angle, (int, float, np.number))

    @patch('street_continuity.util.compute_distance')
    def test_degree_conversion(self, mock_distance):
        """Test that angle is converted from radians to degrees."""
        mock_distance.side_effect = [1.0, 1.0, 1.732]  # ~60 degrees

        angle = compute_angle((0, 0), (1, 0), (0.5, 0.866))

        # Should be in degrees (0-180), not radians (0-π)
        assert 0 <= angle <= 180
        assert angle > np.pi  # If it were in radians, would be <= π
