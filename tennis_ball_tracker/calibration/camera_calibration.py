# Standard library imports
import os
import glob
import json

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

def save_camera_calibration(
    path_to_camera_config_file,
    left_cam,
    right_cam,
    # left_camera_matrix,
    # left_distortion,
    # left_rotation_vectors,
    # left_translation_vectors,
    # right_camera_matrix,
    # right_distortion,
    # right_rotation_vectors,
    # right_translation_vectors,
):
    left_camera_matrix, left_distortion, left_rotation_vectors, left_translation_vectors = left_cam
    right_camera_matrix, right_distortion, right_rotation_vectors, right_translation_vectors = right_cam


    fx = left_camera_matrix[0][0]
    Fx = fx * snickerdoodle_camera_constants.SENSOR_HEIGHT_MM / snickerdoodle_camera_constants.PIXEL_HEIGHT
    fy = left_camera_matrix[1][1]
    Fy = fy * snickerdoodle_camera_constants.SENSOR_WIDTH_MM / snickerdoodle_camera_constants.PIXEL_WIDTH
    left_focal_length = (Fx + Fy) / 2

    fx = right_camera_matrix[0][0]
    Fx = fx * snickerdoodle_camera_constants.SENSOR_HEIGHT_MM / snickerdoodle_camera_constants.PIXEL_HEIGHT
    fy = right_camera_matrix[1][1]
    Fy = fy * snickerdoodle_camera_constants.SENSOR_WIDTH_MM / snickerdoodle_camera_constants.PIXEL_WIDTH
    right_focal_length = (Fx + Fy) / 2

    config = {}
    try:
        with open(path_to_camera_config_file, 'r') as file_:
            config = json.load(file_)
    except:
        pass

    config["focal_length"] = (left_focal_length + right_focal_length) / 2
    # config["baseline"] = None
    # config["tag_size_meters"] = None
    # config["pixel_size"] = None
    config["left_camera_matrix"] = left_camera_matrix.tolist()
    config["right_camera_matrix"] = right_camera_matrix.tolist()
    config["left_distortion_coefficients"] = left_distortion.tolist()
    config["right_distortion_coefficients"] = right_distortion.tolist()

    with open(path_to_camera_config_file, 'w') as file_:
        json.dump(config, file_, indent=2)
    

if __name__ == "__main__":
    import tennis_ball_tracker.snickerdoodle_camera_constants as snickerdoodle_camera_constants
    import tennis_ball_tracker.config as config
    
    print("Calibrating the left camera...")
    calibration_files = config.LEFT_CALIBRATION_IMGS
    left_cam = calibrate_camera(
        calibration_files,
        (8, 6),
        25,
        ".png"
    )
    camera_matrix, distortion, _, _ = left_cam
    print("Intrinsic Camera Matrix")
    print(camera_matrix)
    print("Distortion coefficients")
    print(distortion)

    fx = camera_matrix[0][0]
    Fx = fx * snickerdoodle_camera_constants.SENSOR_HEIGHT_MM / snickerdoodle_camera_constants.PIXEL_HEIGHT
    fy = camera_matrix[1][1]
    Fy = fy * snickerdoodle_camera_constants.SENSOR_WIDTH_MM / snickerdoodle_camera_constants.PIXEL_WIDTH
    print("Focal length: " + str((Fx + Fy) / 2))
    print("Expected Focal length: " + str(snickerdoodle_camera_constants.EXPECTED_FOCAL_LENGTH_MM))


    print("Calibrating the right camera...")
    calibration_files = config.RIGHT_CALIBRATION_IMGS
    right_cam = calibrate_camera(
        calibration_files,
        (8, 6),
        25,
        ".png"
    )
    camera_matrix, distortion, _, _ = right_cam
    print("Intrinsic Camera Matrix")
    print(camera_matrix)
    print("Distortion coefficients")
    print(distortion)

    fx = camera_matrix[0][0]
    Fx = fx * snickerdoodle_camera_constants.SENSOR_HEIGHT_MM / snickerdoodle_camera_constants.PIXEL_HEIGHT
    fy = camera_matrix[1][1]
    Fy = fy * snickerdoodle_camera_constants.SENSOR_WIDTH_MM / snickerdoodle_camera_constants.PIXEL_WIDTH
    print("Focal length: " + str((Fx + Fy) / 2))
    print("Expected Focal length: " + str(snickerdoodle_camera_constants.EXPECTED_FOCAL_LENGTH_MM))

    save_camera_calibration(
        config.CALIBRATION_CONFIG,
        left_cam,
        right_cam
    )