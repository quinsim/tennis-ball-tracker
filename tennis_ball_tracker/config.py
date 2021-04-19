# Standard library imports
import os
# Third party imports

# Local application imports

LOCAL_IP_ADDRESS = "127.0.0.1"
IP_ADDRESS = "192.168.1.9"
CTRL_PORT = 5561
CAMERA_FEED_PORT = 5562

MODULE = os.path.dirname(__file__)
DEPENDENCIES = os.path.join(os.path.split(MODULE)[0], "dependencies")