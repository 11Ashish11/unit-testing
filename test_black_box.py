import unittest
from speed_controller import SpeedController

class TestSpeedControllerBlackBox(unittest.TestCase):
    """
    Black-box tests for SpeedController.update_speed().

    Design method:
      - Category partition on road_condition and safety_mode.
      - Boundary value analysis (BVA) on traffic_density and slope_angle,
        testing on-point and off-point values on BOTH sides of each
        decision boundary (e.g. 49 / 50 / 51 and 79 / 80 / 81).

    Only NOMINAL (in-range) boundary values are asserted here. Invalid
    boundary values (traffic < 0 or > 100, slope < -10 or > 10) are
    discussed separately: per the requirements they should raise a
    ValueError, but the code currently does not validate ranges.

    Run with:
    python -m unittest test_black_box.py
    """

    def setUp(self):
        """Executed before each test."""
        self.controller = SpeedController(speed_limit=60)

    # ---- Category partition: road_condition -------------------------------

    # valid - road_condition category: clear
    def test_road_clear(self):
        """clear -> factor 1.0 : 60 * 1.0 = 60.00"""
        self.assertEqual(self.controller.update_speed('clear', 0, 0), 60.0)

    # valid - road_condition category: wet
    def test_road_wet(self):
        """wet -> factor 0.80 : 60 * 0.80 = 48.00"""
        self.assertEqual(self.controller.update_speed('wet', 0, 0), 48.0)

    # valid - road_condition category: icy
    def test_road_icy(self):
        """icy -> factor 0.6 : 60 * 0.6 = 36.00"""
        self.assertEqual(self.controller.update_speed('icy', 0, 0), 36.0)

    # invalid - road_condition 'foggy' is not one of clear/wet/icy
    def test_road_invalid_raises(self):
        """An unknown road condition must raise ValueError."""
        with self.assertRaises(ValueError):
            self.controller.update_speed('foggy', 0, 0)

    # ---- BVA: traffic_density, boundary at 50 (code: > 50) ----------------

    # valid - traffic_density boundary at 50: off-point below (49)
    def test_traffic_49_below_boundary(self):
        """49 is NOT > 50 -> no reduction : 60.00"""
        self.assertEqual(self.controller.update_speed('clear', 49, 0), 60.0)

    # valid - traffic_density boundary at 50: on-point (50)
    def test_traffic_50_on_boundary(self):
        """50 is NOT > 50 -> no reduction : 60.00"""
        self.assertEqual(self.controller.update_speed('clear', 50, 0), 60.0)

    # valid - traffic_density boundary at 50: off-point above (51)
    def test_traffic_51_just_over_boundary(self):
        """51 is > 50 and <= 80 -> -10 : 50.00"""
        self.assertEqual(self.controller.update_speed('clear', 51, 0), 50.0)

    # ---- BVA: traffic_density, boundary at 80 (code: > 80) ----------------

    # valid - traffic_density boundary at 80: off-point below (79)
    def test_traffic_79_below_boundary(self):
        """79 is > 50 and <= 80 -> -10 : 50.00"""
        self.assertEqual(self.controller.update_speed('clear', 79, 0), 50.0)

    # valid - traffic_density boundary at 80: on-point (80)
    def test_traffic_80_on_boundary(self):
        """80 is <= 80 -> -10 : 50.00"""
        self.assertEqual(self.controller.update_speed('clear', 80, 0), 50.0)

    # valid - traffic_density boundary at 80: off-point above (81)
    def test_traffic_81_just_over_boundary(self):
        """81 is > 80 -> -20 : 40.00"""
        self.assertEqual(self.controller.update_speed('clear', 81, 0), 40.0)

    # ---- BVA: traffic_density, nominal range ends 0 and 100 ---------------

    # valid - traffic_density range minimum (0)
    def test_traffic_0_min(self):
        """0 (min) -> no reduction : 60.00"""
        self.assertEqual(self.controller.update_speed('clear', 0, 0), 60.0)

    # valid - traffic_density range maximum (100)
    def test_traffic_100_max(self):
        """100 (max) is > 80 -> -20 : 40.00"""
        self.assertEqual(self.controller.update_speed('clear', 100, 0), 40.0)

    # ---- BVA: slope_angle, boundary at 0 (uphill / downhill) --------------
    # Uses 'wet' (base 48) so the uphill increase is visible and not clamped.

    # valid - slope_angle boundary at 0: off-point below / downhill (-1)
    def test_slope_minus1_downhill(self):
        """-1 downhill -> -1 : 48 - 1 = 47.00"""
        self.assertEqual(self.controller.update_speed('wet', 0, -1), 47.0)

    # valid - slope_angle boundary at 0: on-point / flat (0)
    def test_slope_0_flat(self):
        """0 -> no slope adjustment : 48.00"""
        self.assertEqual(self.controller.update_speed('wet', 0, 0), 48.0)

    # valid - slope_angle boundary at 0: off-point above / uphill (+1)
    def test_slope_plus1_uphill(self):
        """+1 uphill -> +1 : 48 + 1 = 49.00"""
        self.assertEqual(self.controller.update_speed('wet', 0, 1), 49.0)

    # ---- BVA: slope_angle, nominal range ends -10 and +10 -----------------

    # valid - slope_angle range minimum / downhill (-10)
    def test_slope_minus10_min(self):
        """-10 (min) downhill -> -10 : 48 - 10 = 38.00"""
        self.assertEqual(self.controller.update_speed('wet', 0, -10), 38.0)

    # valid - slope_angle range maximum / uphill (+10)
    def test_slope_plus10_max(self):
        """+10 (max) uphill -> +10 : 48 + 10 = 58.00"""
        self.assertEqual(self.controller.update_speed('wet', 0, 10), 58.0)

    # ---- Category partition: safety_mode ----------------------------------

    # valid - safety_mode category: enabled
    def test_safety_mode_enabled_clamps(self):
        """Safety on clamps to speed_limit - 10 : min(60, 50) = 50"""
        self.controller.set_safety_mode(True)
        self.assertEqual(self.controller.update_speed('clear', 0, 0), 50)

    # valid - safety_mode category: disabled
    def test_safety_mode_disabled_caps_at_limit(self):
        """Safety off: uphill 60 + 10 = 70 is capped at speed_limit 60 : 60.00"""
        self.controller.set_safety_mode(False)
        self.assertEqual(self.controller.update_speed('clear', 0, 10), 60.0)


if __name__ == "__main__":
    unittest.main()
