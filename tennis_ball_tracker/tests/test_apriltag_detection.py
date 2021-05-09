# Standard library imports
import json
import unittest

# Third party imports

# Local application imports
import tennis_ball_tracker.apriltag_detection as apriltag_detection
from tennis_ball_tracker.CameraFeed import CameraFeed


def read_json(file_):
    with open(file_) as outfile:
        config = json.load(outfile)
    return config

# class test_apriltag_detection(unittest.TestCase):
class test_apriltag_detection():
    def setUp(self):
        import tennis_ball_tracker.config as config

        self.config = read_json(config.CALIBRATION_CONFIG)
        self.camera = CameraFeed()

    def tearDown(self):
        self.config = None

        del self.camera
        self.camera = None

    def test(self):
        self.setUp()
        import numpy as np

        while True:
            left, right = self.camera.getStereoFrames()

            apriltags_left = apriltag_detection.findAprilTags(left)
            apriltags_right = apriltag_detection.findAprilTags(right)

            if apriltags_left and apriltags_right:
                pose_left = apriltag_detection.determine_camera_pose(apriltags_left[:1], self.config["tag_size_meters"], self.config["left_camera_matrix"])[0]
                pose_right = apriltag_detection.determine_camera_pose(apriltags_right[:1], self.config["tag_size_meters"], self.config["right_camera_matrix"])[0]

                X, Y, Z = apriltag_detection.determine_camera_xyz(
                    apriltags_left[:1],
                    apriltags_right[:1],
                    self.config["focal_length"],
                    self.config["baseline"],
                    self.config["pixel_size"],
                    self.config["left_camera_matrix"],
                    self.config["right_camera_matrix"],
                )[0]

                camPt = np.array([X, Y, Z, 1]).T
                position = np.dot(np.linalg.inv(pose_left[0]), camPt)
                positionCentimeters = position[0:3] * 100
                print(positionCentimeters)

        self.tearDown()

if __name__ == "__main__":
    t = test_apriltag_detection()
    t.test()