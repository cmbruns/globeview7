from math import radians
import unittest

from gv.projection import WGS84Projection
from gv.view_state import ViewState


class TestDragLatitude(unittest.TestCase):
    def setUp(self):
        self.view_state = ViewState()
        self.view_state.window_size = 100, 100
        self.view_state._projection = WGS84Projection()

    def test_drag_lat_past_pole(self):
        # Tilt earth forward so we can see past the north pole
        v = self.view_state
        v.center_location = radians(0), radians(45)
        dwin = (0, 10)  # Drag earth downward, so center latitude should increase
        self.assertGreater(dwin[1], 0)  # Positive shift is downward in win frame
        self.assertEqual(dwin[0], 0)
        dnmc = v.nmc_J_win @ dwin
        self.assertLess(dnmc[1], 0)  # Negative shift is downward in nmc frame
        self.assertEqual(dnmc[0], 0)
        pnmcA = (0, 0.90, 1)  # drag point "A" is above the north pole
        dobqA = v._projection.dobq_for_dnmc(dnmc, pnmcA)
        self.assertEqual(dobqA[1], 0)  # right
        self.assertGreater(dobqA[0], 0)  # thither
        self.assertLess(dobqA[2], 0)  # up
        decfA = v.ecf_J_obq @ dobqA
        x = 3
