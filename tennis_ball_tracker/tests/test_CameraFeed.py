# Standard library imports
import unittest

# Third party imports
import numpy as np

# Local application imports
from tennis_ball_tracker.CameraFeed import CameraFeed, Frame

class MockCameraFeed(CameraFeed):

    def getStereoFrames(self):
        # See parent docstring
        frame_ = np.full((480, 752, 4), fil_value=[1, 2, 3, 4], dtype=np.uint8)
        return Frame(frame_), Frame(frame_)

    def actuallyGetStereoFrames(self):
        return super(CameraFeed, self).getStereoFrames()

    actuallyGetStereoFrames.__doc__ = getStereoFrames.__doc__

class test_CameraFeed(unittest.TestCase):
    EXPECTED_ALL = np.full((480, 752, 4), fil_value=[1, 2, 3, 4], dtype=np.uint8)
    EXPECTED_RGB = np.full((480, 752, 3), fil_value=[1, 2, 3], dtype=np.uint8)
    EXPECTED_BLUE = np.full((480, 752, 1), fil_value=1, dtype=np.uint8)
    EXPECTED_GREEN = np.full((480, 752, 1), fil_value=2, dtype=np.uint8)
    EXPECTED_RED = np.full((480, 752, 1), fil_value=3, dtype=np.uint8)
    EXPECTED_GREY = np.full((480, 752, 1), fil_value=4, dtype=np.uint8)
    
    def setUp(self):
        self.camera = CameraFeed()

    def tearDown(self):
        del self.camera

    def test_actuallyGetStereoFrames(self):
        left, right = self.camera.actuallyGetStereoFrames()
        self.assertIsInstance(left, Frame)
        self.assertTrue(left.ALL.shape == self.EXPECTED_ALL.shape)

        self.assertIsInstance(right, Frame)
        self.assertTrue(right.ALL.shape == self.EXPECTED_ALL.shape)

    def test_getStereoFrames(self):
        left, right = self.camera.getStereoFrames()
        self.assertTrue(np.array_equal(left, self.EXPECTED_ALL))
        self.assertTrue(np.array_equal(right, self.EXPECTED_ALL))

    def test_getStereoAll(self):
        left, right = self.camera.getStereoAll()
        self.assertTrue(np.array_equal(left, self.EXPECTED_ALL))
        self.assertTrue(np.array_equal(right, self.EXPECTED_ALL))

    def test_getStereoRGB(self):
        left, right = self.camera.getStereoRGB()
        self.assertTrue(np.array_equal(left, self.EXPECTED_RGB))
        self.assertTrue(np.array_equal(right, self.EXPECTED_RGB))

    def test_getStereoRed(self):
        left, right = self.camera.getStereoRed()
        self.assertTrue(np.array_equal(left, self.EXPECTED_RED))
        self.assertTrue(np.array_equal(right, self.EXPECTED_RED))

    def test_getStereoGreen(self):
        left, right = self.camera.getStereoGreen()
        self.assertTrue(np.array_equal(left, self.EXPECTED_GREEN))
        self.assertTrue(np.array_equal(right, self.EXPECTED_GREEN))

    def test_getStereoBlue(self):
        left, right = self.camera.getStereoBlue()
        self.assertTrue(np.array_equal(left, self.EXPECTED_BLUE))
        self.assertTrue(np.array_equal(right, self.EXPECTED_BLUE))

    def test_getStereoGrey(self):
        left, right = self.camera.getStereoGrey()
        self.assertTrue(np.array_equal(left, self.EXPECTED_GREY))
        self.assertTrue(np.array_equal(right, self.EXPECTED_GREY))

    def file_exists(self, path):
        import os
        self.assertTrue(os.path.exists(path))

    def open_image(self, path):
        import cv2
        cv2.imread(path)
        raise NotImplementedError()

    def test_saveStereoFrame(self):
        path = "/tmp/test.bmp"

        left, _ = self.test_getStereoAll()
        self.camera.saveStereoFrame("/tmp/test.bmp", left)
        self.file_exists(path)

        # self.assertTrue(np.array_equal(left, self.EXPECTED_ALL))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_ALL))

    def test_saveStereoAll(self):
        path = "/tmp/test.bmp"
        left_path = "/tmp/left_test.bmp"
        right_path = "/tmp/right_test.bmp"

        self.camera.saveStereoAll(path)
        self.file_exists(left_path)
        self.file_exists(right_path)
        # self.assertTrue(np.array_equal(left, self.EXPECTED_ALL))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_ALL))

    def test_saveStereoRGB(self):
        path = "/tmp/test.bmp"
        left_path = "/tmp/left_test.bmp"
        right_path = "/tmp/right_test.bmp"

        self.camera.saveStereoRGB(path)
        self.file_exists(left_path)
        self.file_exists(right_path)
        # self.assertTrue(np.array_equal(left, self.EXPECTED_RGB))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_RGB))

    def test_saveStereoRed(self):
        path = "/tmp/test.bmp"
        left_path = "/tmp/left_test.bmp"
        right_path = "/tmp/right_test.bmp"

        self.camera.saveStereoRed(path)
        self.file_exists(left_path)
        self.file_exists(right_path)
        # self.assertTrue(np.array_equal(left, self.EXPECTED_RED))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_RED))

    def test_saveStereoGreen(self):
        path = "/tmp/test.bmp"
        left_path = "/tmp/left_test.bmp"
        right_path = "/tmp/right_test.bmp"

        self.camera.saveStereoGreen(path)
        self.file_exists(left_path)
        self.file_exists(right_path)
        # self.assertTrue(np.array_equal(left, self.EXPECTED_GREEN))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_GREEN))

    def test_saveStereoBlue(self):
        path = "/tmp/test.bmp"
        left_path = "/tmp/left_test.bmp"
        right_path = "/tmp/right_test.bmp"

        self.camera.saveStereoBlue(path)
        self.file_exists(left_path)
        self.file_exists(right_path)
        # self.assertTrue(np.array_equal(left, self.EXPECTED_BLUE))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_BLUE))

    def test_saveStereoGrey(self):
        path = "/tmp/test.bmp"
        left_path = "/tmp/left_test.bmp"
        right_path = "/tmp/right_test.bmp"

        self.camera.saveStereoGrey(path)
        self.file_exists(left_path)
        self.file_exists(right_path)
        # self.assertTrue(np.array_equal(left, self.EXPECTED_GREY))
        # self.assertTrue(np.array_equal(right, self.EXPECTED_GREY))
