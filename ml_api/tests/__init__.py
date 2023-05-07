import unittest
from tests.test_detection import TestDetection
from tests.test_geometry import *

# Test suite for all tests
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestGeometry())
    suite.addTest(TestDetection())
    return suite
