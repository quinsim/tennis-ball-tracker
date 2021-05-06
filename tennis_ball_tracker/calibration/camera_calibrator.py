# Standard library imports
import os
import glob
import uuid
import time
import tempfile
import threading
from Queue import Queue

# Third party imports
import cv2

# Local application imports
from tennis_ball_tracker.CameraFeed import CameraFeed
import tennis_ball_tracker.config as config

message_queue = Queue(-1)
lock = threading.Event()
lock.set()

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

    def __init__(self, grid_pattern, path_to_store_imgs = config.CALIBRATION_FOLDERS, img_ext = ".png", use_circle_grid = False,  camera = None):
        super(CameraCalibrator, self).__init__(name="Camera Calibrator")
        self.LEFT_PATH = os.path.join(path_to_store_imgs, "left")
        self.RIGHT_PATH = os.path.join(path_to_store_imgs, "right")

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
        file_ = os.path.join(path_to_store_imgs, "cal-" + str(uuid.uuid1()) + img_ext)
        message_queue.put("Saving captured calibration image " + file_ + "...")
        self.camera.saveStereoFrame(file_, img)

    def remove_stale_calibration_files(self, path_to_store_imgs):
        """
        Remove all stale calibration files.

        Args:
            path_to_store_imgs (str): Path where calibration files may be stored.
        """        
        message_queue.put("Clearing any sale calibration files in " + path_to_store_imgs + "...")
        if os.path.isdir(path_to_store_imgs):
            images = glob.glob(os.path.join(path_to_store_imgs, "*"))
            [os.remove(image) for image in images]
            os.rmdir(path_to_store_imgs)

    def setup_calibration_folders(self, path_to_store_imgs):
        """
        Create calibration folders.
        
        These folders will hold the camera calibration files.

        Args:
            path_to_store_imgs (str): Path where calibration files may be stored.
        """
        message_queue.put("Creating the calibration folder " + path_to_store_imgs + "...")
        if not os.path.isdir(path_to_store_imgs):
            os.mkdir(path_to_store_imgs)

    def run(self):
        """Run the camera calibration process."""
        message_queue.put("Starting the Camera Calibration process...")

        self.remove_stale_calibration_files(self.LEFT_PATH)
        self.remove_stale_calibration_files(self.RIGHT_PATH)
        self.setup_calibration_folders(self.LEFT_PATH)
        self.setup_calibration_folders(self.RIGHT_PATH)

        valid_imgs = 0
        while (valid_imgs != self.REQUIRED_NUMBER_OF_IMGS):
            message_queue.put("Attempting to acquire images {} out of {}...".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
            left, right = self.camera.getStereoRGB()
            left_greyscale = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
            right_greyscale = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

            message_queue.put("Validating images {} out of {}...".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
            if (self.verify_pattern(left_greyscale, self.grid_pattern) and self.verify_pattern(right_greyscale, self.grid_pattern)):
                message_queue.put("Images {} out of {} are valid!".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
                self.save_calibration_image(self.LEFT_PATH, self.img_ext, left)
                self.save_calibration_image(self.RIGHT_PATH, self.img_ext, right)
                valid_imgs+= 1
            else:
                message_queue.put("Images {} out of {} are invalid!".format(valid_imgs+1, self.REQUIRED_NUMBER_OF_IMGS))
            message_queue.put("Please move the checkerboard in preporation of our next calibration image...")
            lock.clear()
            lock.wait()

        message_queue.put("Camera Calibration process complete!")

if __name__ == "__main__":
    calibrator = CameraCalibrator((8, 6))
    calibrator.start()
    while calibrator.is_alive():
        if not message_queue.empty():
            msg = message_queue.get(True)
            print(msg)
        if not lock.is_set():
            raw_input("Press enter to capture the next calibration img")
            lock.set()
    calibrator.join()