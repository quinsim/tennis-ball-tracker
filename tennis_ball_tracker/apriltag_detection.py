# Standard library imports
import numpy as np

# Third party imports
import cv2
import apriltag

# Local application imports
from tennis_ball_tracker.CameraFeed import Frame

BLUE = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
RED = (0x00, 0x00, 0xFF)

WHITE = (0x00, 0x00, 0x00)
BLACK = (0xFF, 0xFF, 0xFF)

detector = apriltag.Detector()

def findAprilTags(
    frame,
    mark_corners = False,
    mark_edges = False,
):
    """
    Find all apriltags in an image and outline them if requested.

    Args:
        frame (Frame): The image frame.
        mark_corners (bool, optional): Mark the corners with a red dot? Defaults to False.
        mark_edges (bool, optional): Mark the edges with a red line? Defaults to False.
    
    Returns:
        Frame: The modified frame.
    """
    assert isinstance(frame, Frame)
    apriltags = detector.detect(frame.GREYSCALE)
    return apriltags


def mark_apriltag_corners(img, apriltags):
    """
    Mark the 4 corners of the detected apriltags with a red dot.

    Args:
        img ([type]): The image.
        apriltags (List[apriltag.Detection]): The detected apriltags.

    Returns:
        [type]: The modified image.
    """
    for apriltag in apriltags:
        for corner in apriltag.corners:
            corner = [int(c) for c in corner]
            cv2.circle(img, tuple(corner), 3, RED, -1)

    return img


def mark_apriltag_edges(img, apriltags):
    """
    Outline the 4 edges of the detected apriltags with a red line.

    Args:
        img ([type]): The image.
        apriltags (List[apriltag.Detection]): The detected apriltags.

    Returns:
        [type]: The modified image.
    """
    for apriltag in apriltags:
        corners = apriltag.corners
        for edge1, edge2 in zip(corners, list(corners[1:]) + list(corners[:1])):
            edge1 = [int(c) for c in edge1]
            edge2 = [int(c) for c in edge2]
            cv2.line(img, tuple(edge1), tuple(edge2), RED, 3)

    return img


def determine_camera_pose(
    apriltags,
    tag_size_meters,
    camera_matrix,
):
    """
    Determine the pose of the camera with respect to each of the detected apriltags.

    Args:
        apriltags (List[apriltag.Detection]): The apriltags detected by the camera.
        tag_size_meters (float): The tag size in meters. Apriltags are squares.
        camera_matrix (List[List[float]]): The 3 x 3 camera matrix of the camera.
    """
    camera_params = (
        camera_matrix[0][0],
        camera_matrix[1][1],
        camera_matrix[0][2],
        camera_matrix[1][2],
    )
    camera_poses = []
    for apriltag in apriltags:
        pose = detector.detection_pose(apriltag, camera_params, tag_size_meters, 1)
        camera_poses.append(pose)

    return camera_poses


def determine_camera_xyz(
    apriltags_left,
    apriltags_right,
    focal_length,
    baseline,
    pixel_size,
    camera_matrix_left,
    camera_matrix_right,
):
    """
    Determine the X, Y, Z camera coordinates of each of the detected apriltags.

    NOTE: The Z coordinates are determined with both cameras but the X and Y are
    determined with just the left camera. Utilizing both camera may improve accuracy.

    Args:
        apriltags_left (List[apriltag.Detection]): The apriltags detected by the left camera.
        apriltags_right (List[apriltag.Detection]): The apriltags detected by the right camera.
        focal_length (float): The focal lengths of the left and right camera.
        baseline (float): 
        pixel_size (float): 
        camera_matrix_left (List[List[float]]): The 3 x 3 camera matrix of the left camera.
        camera_matrix_right (List[List[float]]): The 3 x 3 camera matrix of the right camera.
    """
    assert (len(apriltags_left) == len(apriltags_right))
    x_principal_left, y_principal_left = (camera_matrix_left[0][2], camera_matrix_left[1][2])
    x_principal_right, y_principal_right = (camera_matrix_right[0][2], camera_matrix_right[1][2])

    xyz_camera_coordinates = []
    for apriltag_left, apriltag_right in zip(apriltags_left, apriltags_right):
        x_left, y_left = apriltag_left.corners[0]
        x_right, y_right = apriltag_right.corners[0]

        Z = (baseline * focal_length) / (abs((x_left - x_principal_left) - (x_right - x_principal_right)) * pixel_size)
        X = (Z * (x_left - x_principal_left) * pixel_size) / focal_length # take left and right avg?
        Y = (Z * (y_left - y_principal_left) * pixel_size) / focal_length # take left and right avg?
        xyz_camera_coordinates.append((X / 1000, Y / 1000, Z / 1000)) # Convert to meters

    return xyz_camera_coordinates


if __name__ == "__main__":
    import numpy as np
    from tennis_ball_tracker.CameraFeed import CameraFeed

    config = {
        "focal_length": 5.878,
        "baseline": 58.8104,
        "tag_size_meters": 0.1,
        "pixel_size": 0.006,
        "left_camera_matrix": [
            [984.7575, 0, 310.7146],
            [0, 983.0474, 261.7735],
            [0, 0, 1]
        ],
        "right_camera_matrix": [
            [977.0625, 0, 346.9222],
            [0, 975.8967, 290.9704],
            [0, 0, 1]
        ],
        "left_distortion_coefficients": [-0.3084, -0.1320, 0, 0],
        "right_distortion_coefficients": [-0.3012, -1.7047, 0, 0]
    }

    camera = CameraFeed()
    while True:
        left, right = camera.getStereoFrames()
        apriltags_left = findAprilTags(left)
        apriltags_right = findAprilTags(right)

        if apriltags_left and apriltags_right:

            pose_left = determine_camera_pose(apriltags_left[:1], config["tag_size_meters"], config["left_camera_matrix"])[0]
            pose_right = determine_camera_pose(apriltags_right[:1], config["tag_size_meters"], config["right_camera_matrix"])[0]

            X, Y, Z = determine_camera_xyz(
                apriltags_left[:1],
                apriltags_right[:1],
                config["focal_length"],
                config["baseline"],
                config["pixel_size"],
                config["left_camera_matrix"],
                config["right_camera_matrix"],
            )[0]

            camPt = np.array([X, Y, Z, 1]).T
            position = np.dot(np.linalg.inv(pose_left[0]), camPt)
            positionCentimeters = position[0:3] * 100
            print(positionCentimeters)
        else:
            print("No apriltags detected")
