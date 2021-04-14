# Standard library imports
from collections import namedtuple
# Third party imports

# Local application imports

COMMAND = "command"

"""Command strings."""
CMD_STATUS = "status"
CMD_START_TRACKING_TENNISBALL = "start_tracking_tennisball"
CMD_STOP_TRACKING_TENNISBALL = "stop_tracking_tennisball"
CMD_CALIBRATE_CAMERA = "calibrate_camera"
CMD_GET_TENNISBALL_COORDS = "get_tennisball_coords"
CMD_CONFIGURE_LED = "configure_led"
CMD_GET_TENNISCOURT_BOUNDARIES_REQ = "get_tenniscourt_boundaries_req"
CMD_GET_TENNISCOURT_BOUNDARIES_REP = "get_tenniscourt_boundaries_rep"

"""DEBUG COMMANDS"""
CMD_START_SENDING_CAMERA_FEED = "start_sending_camera_feed"
CMD_STOP_SENDING_CAMERA_FEED = "stop_sending_camera_feed"
CMD_GET_CAMERA_FEED = "get_camera_feed_req"
CMD_CAMERA_FEED_DATA = "camera_feed_data"
CMD_TEST_CAMERA_FPS_REQ = "test_camera_fps_req"
CMD_TEST_CAMERA_FPS_REP = "test_camera_fps_rep"