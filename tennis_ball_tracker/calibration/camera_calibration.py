# Standard library imports
import os
import glob

# Third party imports
import cv2
import numpy as np

# Local application imports

class CalibrationError(Exception):
    pass


def calibrate_camera(path_to_img, grid_pattern, checkerboard_square_size_mm = 25, img_ext = ".png", use_circle_grid = False):
    """
    Calibrate a camera using a set of calibration images.

    The camera can be calibrates using images of a  ```Chessboard Grid``` or a ```Circle Grid```.

    NOTE: The checkerboard_square_size_mm will only effect the extrinsic parameters (rotational_vectors, translation_vectors).

    Args:
        path_to_img (str): Path to the calibration images.
        grid_pattern (Tuple[int, int]): The pattern of your calibration grid.
        checkerboard_square_size_mm (int, optional): The square size of your calibration checkerboard in millimeters
        img_ext (str, optional): The image extention of the calibration images. Defaults to ```.png```.
        use_circle_grid (bool, optional): Whether a circular grid pattern is used for calibration. Defaults to False.

    Returns:
        Tuple[matrix[3x3], matrix[1x5], matrix[], matrix[]]: (camera matrix (3x3), distortion (1x5), rotational_vectors (), translation_vectors ())
    """
    assert (os.path.isdir(path_to_img))

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare the object points. (0, 0, 0), (1, 0, 0), (2, 0, 0), ... (grid_pattern[0]-1, grid_pattern[1]-1, 0)
    empty_obj_point = np.zeros((grid_pattern[0] * grid_pattern[1], 3), np.float32)
    grid = np.mgrid[0:grid_pattern[0], 0:grid_pattern[1]] * checkerboard_square_size_mm
    empty_obj_point[:,:2] = grid.T.reshape(-1, 2)

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
            corners_ = cv2.cornerSubPix(greyscale_img, corners, (11, 11), (-1, -1), criteria)
            img_points.append(corners_)
        else:
            print(img_path + " is an invalid calibration image.")

    ret, camera_matrix, distortion, rotation_vectors, translation_vectors = cv2.calibrateCamera(obj_points, img_points, greyscale_img.shape[::-1], None, None)

    if not ret:
        raise CalibrationError("Failed to calibrate the camera with the given images.")

    return camera_matrix, distortion, rotation_vectors, translation_vectors

if __name__ == "__main__":
    import os
    import tempfile
    import tennis_ball_tracker.snickerdoodle_camera_constants as snickerdoodle_camera_constants

    print("Calibrating the left camera...")
    calibration_files = os.path.join(tempfile.gettempdir(), "left")
    camera_matrix, distortion, _, _ = calibrate_camera(
        calibration_files,
        (8, 6),
        25,
        ".png"
    )
    print("Intrinsic Camera Matrix")
    print(camera_matrix)
    print("Distortion coefficients")
    print(distortion)

    fx = camera_matrix[0][0]
    Fx = fx * snickerdoodle_camera_constants.SENSOR_HEIGHT_MM / snickerdoodle_camera_constants.PIXEL_HEIGHT
    fy = camera_matrix[1][1]
    Fy = fy * snickerdoodle_camera_constants.SENSOR_WIDTH_MM / snickerdoodle_camera_constants.PIXEL_WIDTH
    print("Focal length: " + str((Fx + Fy) / 2))
    print("Expected Focal length: " + snickerdoodle_camera_constants.EXPECTED_FOCAL_LENGTH_MM)


    print("Calibrating the right camera...")
    calibration_files = os.path.join(tempfile.gettempdir(), "right")
    camera_matrix, distortion, _, _ = calibrate_camera(
        calibration_files,
        (8, 6),
        25,
        ".png"
    )
    print("Intrinsic Camera Matrix")
    print(camera_matrix)
    print("Distortion coefficients")
    print(distortion)

    fx = camera_matrix[0][0]
    Fx = fx * snickerdoodle_camera_constants.SENSOR_HEIGHT_MM / snickerdoodle_camera_constants.PIXEL_HEIGHT
    fy = camera_matrix[1][1]
    Fy = fy * snickerdoodle_camera_constants.SENSOR_WIDTH_MM / snickerdoodle_camera_constants.PIXEL_WIDTH
    print("Focal length: " + str((Fx + Fy) / 2))
    print("Expected Focal length: " + snickerdoodle_camera_constants.EXPECTED_FOCAL_LENGTH_MM)