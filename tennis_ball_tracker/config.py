# Standard library imports
import os
import tempfile

# Third party imports

# Local application imports

LOCAL_IP_ADDRESS = "127.0.0.1"
IP_ADDRESS = "192.168.1.5"
CTRL_PORT = 5561
CAMERA_FEED_PORT = 5562

MODULE = os.path.dirname(os.path.abspath(__file__))
DEPENDENCIES = os.path.join(os.path.dirname(MODULE), "dependencies")

CALIBRATION_CONFIG = os.path.join(DEPENDENCIES, "cameraCalibration.json")
CALIBRATION_FOLDERS = tempfile.gettempdir()
LEFT_CALIBRATION_IMGS = os.path.join(CALIBRATION_FOLDERS, "left")
RIGHT_CALIBRATION_IMGS = os.path.join(CALIBRATION_FOLDERS, "right")
CALIBRATION_GRID_PTRN = (8, 6)