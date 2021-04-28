# Standard library imports
import os
import uuid
import time
import tempfile
import threading
from Queue import Queue

# Third party imports
import cv2

# Local application imports
from tennis_ball_tracker.CameraFeed import CameraFeed


message_queue = Queue(-1)
lock = threading.Event()

class CameraCalibrator(threading.Thread):
    """
    Camera Calibrator Module.

    The purpose of this module is to calibrate the snickerdoodle's camera.

    NOTE: If no CameraFeed is provided, one will be instantiated.

    Args:
        path_to_store_imgs (str, optional): Path to store the calibration images. Defaults to the ```temp directory```.
        grid_pattern (Tuple[int, int]): The pattern of your calibration grid.
        img_ext (str, optional): The image extention to use for the calibration images. Defaults to ```.png```.
        use_circle_grid (bool, optional): Whether a circular grid pattern is being used for calibration. Defaults to False.
        camera (CameraFeed, optional): The CameraFeed obj. Defaults to None.
    """
    REQUIRED_NUMBER_OF_IMGS = 20

    def __init__(self, grid_pattern, path_to_store_imgs = tempfile.gettempdir(), img_ext = ".png", use_circle_grid = False,  camera = None):
        super(CameraCalibrator, self).__init__(name="Camera Calibrator")
        self.path_to_store_imgs = path_to_store_imgs
        self.grid_pattern = grid_pattern
        self.img_ext = img_ext
        self.use_circle_grid = use_circle_grid
        if camera is None:
            camera = CameraFeed()
        self.camera = camera

    def verify_pattern(self, greyscale_img, grid_pattern):
        """
        Verify that a given image matches the desired checkerboard pattern.

        Args:
            greyscale_img (): The greyscale image.
            grid_pattern (Tuple[int, int]): The desired checkerboard pattern.
        
        Returns:
            bool: Whether the greyscale image matches the checkerboard pattern.
        """
        ret, _ = cv2.findChessboardCorners(greyscale_img, tuple(grid_pattern))
        return ret
    
    def save_calibration_image(self, path_to_store_imgs, img_ext, img):
        """
        Save a calibration image.

        Args:
            path_to_store_imgs (str): Path to store the calibration images.
            img_ext (str): The image extention to use for the calibration images.
            img (): The image to store.
        """
        file_ = os.path.join(path_to_store_imgs, str(uuid.uuid3) + img_ext)
        self.camera.saveStereoFrame(file_, img)

    def remove_stale_calibration_files(self, path_to_store_imgs):
        """
        Remove all stale calibration files.

        Args:
            path_to_store_imgs (str): Path where calibration files may be stored.
        """
        LEFT_PATH = os.path.join(path_to_store_imgs, "left")
        RIGHT_PATH = os.path.join(path_to_store_imgs, "right")
        
        if os.path.isdir(LEFT_PATH):
            os.rmdir(LEFT_PATH)
        if os.path.isdir(RIGHT_PATH):
            os.rmdir(RIGHT_PATH)

    def run(self):
        """Run the camera calibration process."""
        message_queue.put("Starting the Camera Calibration process...")

        LEFT_PATH = os.path.join(self.path_to_store_imgs, "left")
        RIGHT_PATH = os.path.join(self.path_to_store_imgs, "right")

        message_queue.put("Clearing any sale calibration files...")

        self.remove_stale_calibration_files(self.path_to_store_imgs)

        valid_imgs = 0
        while (valid_imgs != self.REQUIRED_NUMBER_OF_IMGS):
            message_queue.put("Attempting to acquire images {} out of {}...".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
            left, right = self.camera.getStereoFrames()

            message_queue.put("Validating images {} out of {}...".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
            if (self.verify_pattern(left.GREYSCALE, self.grid_pattern) and self.verify_pattern(right.GREYSCALE, self.grid_pattern)):
                message_queue.put("Images {} out of {} are valid!".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
                message_queue.put("Saving the captured calibration images {} out of {}...".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
                self.save_calibration_image(LEFT_PATH, self.img_ext, left.RGB)
                self.save_calibration_image(RIGHT_PATH, self.img_ext, right.RGB)
                valid_imgs+= 1
            else:
                message_queue.put("Images {} out of {} are invalid!".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
            message_queue.put("Please the checkerboard in preporation of our next calibration image...")
            time.sleep(5)
            # lock.wait()

        message_queue.put("Camera Calibration process complete!")

if __name__ == "__main__":
    calibrator = CameraCalibrator((7,7))
    calibrator.start()
    while calibrator.is_alive():
        msg = message_queue.get(True)
        print(msg)
    calibrator.join()