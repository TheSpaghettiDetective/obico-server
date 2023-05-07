import unittest
from lib.geometry import *


class TestGeometry(unittest.TestCase):
    def test_box(self):
        b1 = Box(1.0, 2.0, 1.0, 2.0)
        b2 = Box(2.0, 3.0, 1.0, 2.0)
        b3 = Box(1.0, 2.0, 2.0, 2.0)
        iou_1_2 = b1.calc_iou(b2)
        iou_1_3 = b1.calc_iou(b3)

        self.assertAlmostEqual(iou_1_2, 0.0)
        self.assertAlmostEqual(iou_1_3, 0.5)

