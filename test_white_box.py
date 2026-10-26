import unittest
from speed_controller import SpeedController

class TestSpeedControllerWhiteBox(unittest.TestCase):
    """
    Run with:
        python -m unittest test_white_box.py
    Coverage:
        coverage run -m unittest test_white_box.py
        coverage report -m
    """

    def test_wet_highTraffic_uphill_safetyOn(self):
        """
        Covers: 'wet' branch, traffic > 50 and > 80 (-20),
        slope > 0 (uphill), and safety_mode ENABLED branch.
        60*0.80=48 -> -20=28 -> +5=33 -> min(33,50)=33.00
        """
        c = SpeedController(speed_limit=60)
        c.set_safety_mode(True)
        self.assertEqual(c.update_speed('wet', 90, 5), 33.0)

    def test_icy_midTraffic_downhill_safetyOff(self):
        """
        Covers: 'icy' branch, traffic > 50 and <= 80 (-10),
        slope < 0 (downhill), and safety_mode DISABLED branch.
        60*0.6=36 -> -10=26 -> -5=21 -> max(0,min(21,60))=21.00
        """
        c = SpeedController(speed_limit=60)
        c.set_safety_mode(False)
        self.assertEqual(c.update_speed('icy', 60, -5), 21.0)

    def test_clear_lowTraffic_flat(self):
        """
        Covers: 'clear' branch, traffic <= 50 (no reduction),
        slope == 0 (neither uphill nor downhill branch taken).
        60 -> no changes -> 60.00
        """
        c = SpeedController(speed_limit=60)
        self.assertEqual(c.update_speed('clear', 20, 0), 60.0)

    def test_invalid_road_condition_raises(self):
        """
        Covers: the else branch that raises ValueError for an
        unrecognized road condition.
        """
        c = SpeedController(speed_limit=60)
        with self.assertRaises(ValueError):
            c.update_speed('snow', 0, 0)


if __name__ == "__main__":
    unittest.main()
