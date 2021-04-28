# Standard library imports
import os
import glob

# Third party imports
import cv2
import numpy as np

# Local application imports

class CalibrationError(Exception):
    pass


def calibrate_camera(path_to_img, grid_pattern, img_ext = ".png", use_circle_grid = False):
    """
    Calibrate a camera using a set of calibration images.

    The camera can be calibrates using images of a  ```Chessboard Grid``` or a ```Circle Grid```.

    Args:
        path_to_img (str): Path to the calibration images.
        grid_pattern (Tuple[int, int]): The pattern of your calibration grid.
        img_ext (str, optional): The image extention of the calibration images. Defaults to ```.png```.
        use_circle_grid (bool, optional): Whether a circular grid pattern is used for calibration. Defaults to False.

    Returns:
        Tuple[matrix[3x3], matrix[1x5], matrix[], matrix[]]: (camera matrix (3x3), distortion (1x5), rotational_vectors (), translation_vectors ())
    """
    assert (os.path.isdir(path_to_img))

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare the object points. (0, 0, 0), (1, 0, 0), (2, 0, 0), ... (grid_pattern[0]-1, grid_pattern[1]-1, 0)
    empty_obj_point = np.zeroes((grid_pattern[0] * grid_pattern[1], 3), np.float32)
    empty_obj_point[:,:2] = np.mgrid[0:grid_pattern[0], 0:grid_pattern[1]].T.reshape(-1, 2)

    obj_points = [] # 3D points in real world space
    img_points = [] # 2D points in image plane

    images = glob.glob(os.path.join(path_to_img, "*" + img_ext))
    for img_path in images:
        img = cv2.imread(img_path)
        greyscale_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        if use_circle_grid:
            ret, corners = cv2.findCirclesGrid(greyscale_img, tuple(grid_pattern))
        else:
            ret, corners = cv2.findChessboardCorners(greyscale_img, tuple(grid_pattern))

        if ret:
            obj_points.append(empty_obj_point)
            corners_ = cv2.cornersSubPix(greyscale_img, corners, (11, 11), (-1, -1), criteria)
            img_points.append(corners_)

    ret, camera_matrix distortion, rotation_vectors, translation_vectors = cv2.calibrateCamera(obj_points, img_points, grey.shape[::-1], None, None)

    if not ret:
        raise CalibrationError("Failed to calibrate the camera with the given images.")

    return camera_matrix, distortion, rotation_vectors, translation_vectors
