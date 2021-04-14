# Standard library imports

# Third party imports

# Local application imports
from tennis_ball_tracker import api


class sub_message_t(object):
    """
    Defines the requirements of a sub message.
    
    This class implements the ``__iter__`` method for easy
    conversion to a dict.
    """
    def __iter__(self):
        for field, value in self.__dict__.items():
            if isinstance(value, list):
                lst = []
                for i in value:
                    if isinstance(i, sub_message_t):
                        lst.append(dict(i))
                    else:
                        lst.append(i)
                yield field, lst
            elif isinstance(value, sub_message_t):
                yield field, dict(value)
            else:
                yield field, value

    def __str__(self):
        return str(dict(self))

class message_t(sub_message_t):
    """
    Defines the requirements of a message.
    
    This class implements the ``__iter__`` method for easy
    conversion to a dict.
    """
    def __init__(self, command):
        super(message_t, self).__init__()
        self.command = command


class point3D(sub_message_t):
    """
    Defines a 3D Point.

    Args:
        x (float): The x coord.
        y (float): The y coord.
        z (float): The z coord.
    """ 
    def __init__(self, x, y, z):
        super(point3D, self).__init__()
        self.x = x
        self.y = y
        self.z = z


class status_rep(message_t):
    """
    The response for all commands.

    This is received from the REQ server.

    Args:
        cmd_id (str): The command the response is for.
        successful (bool): Whether the cmd was successful.
    
    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, cmd_id, successful, msg="", **kwargs):
        super(status_rep, self).__init__(api.CMD_STATUS)
        self.cmd_id = cmd_id
        self.successful = successful
        self.msg = msg


class start_tracking_req(message_t):
    """
    Instructs the device to start tracking the tennisball.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(start_tracking_req, self).__init__(api.CMD_START_TRACKING_TENNISBALL)


class stop_tracking_req(message_t):
    """
    Instructs the device to stop tracking the tennisball.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(stop_tracking_req, self).__init__(api.CMD_STOP_TRACKING_TENNISBALL)


class calibrate_camera_req(message_t):
    """
    Instructs the device to calibrate the cameras.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(calibrate_camera_req, self).__init__(api.CMD_CALIBRATE_CAMERA)


class configure_led_req(message_t):
    """
    Instructs the device to configure its LED.

    This is sent to the REQ server.

    Args:
        period_ms (int): The period for the flashing LED.
        duty_cycle_percent (int): The flashing duty cycle as a percentage.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, period_ms, duty_cycle_percent, **kwargs):
        super(configure_led_req, self).__init__(api.CMD_CONFIGURE_LED)
        self.period_ms = period_ms
        self.duty_cycle_percent = duty_cycle_percent


class get_tenniscourt_boundaries_req(message_t):
    """
    Instructs the device to get the boundaries of the tenniscourt.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(get_tenniscourt_boundaries_req, self).__init__(api.CMD_GET_TENNISCOURT_BOUNDARIES_REQ)


class get_tenniscourt_boundaries_rep(message_t):
    """
    This is the response from the get_tenniscourt_boundaries_req cmd.

    Args:
        corners (List[points3d]): The 4 corners of the tenniscourt.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, corners, **kwargs):
        super(get_tenniscourt_boundaries_rep, self).__init__(api.CMD_GET_TENNISCOURT_BOUNDARIES_REP)
        # We are expecting corners to be a list of point3D objects.
        # If this is not the case, force the data into a point3D object.
        for corner in list(corners):
            if isinstance(corner, dict):
                corners.append(point3D(**corner))
            else:
                corners.append(corner)
        self.corners = corners

# DEBUG MESSAGES

class start_sending_camera_feed_req(message_t):
    """
    Instructs the device to start sending feed from the left and right camera.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(start_sending_camera_feed_req, self).__init__(api.CMD_START_SENDING_CAMERA_FEED)



class stop_sending_camera_feed_req(message_t):
    """
    Instructs the device to stop sending feed from the left and right camera.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(stop_sending_camera_feed_req, self).__init__(api.CMD_STOP_SENDING_CAMERA_FEED)

class get_camera_feed_req(message_t):
    """
    Instructs the device to send the feed from the left and right camera.

    This is sent to the REQ server.

    Attributes:    
        command (str): The requests command.
    """
    def __init__(self, **kwargs):
        super(get_camera_feed_req, self).__init__(api.CMD_GET_CAMERA_FEED)

class camera_feed_data(message_t):
    TOPIC = "camera.feed"
    def __init__(self, left_feed, right_feed, **kwargs):
        super(camera_feed_data, self).__init__(api.CMD_CAMERA_FEED_DATA)
        self.left_feed = left_feed
        self.right_feed = right_feed

    def __str__(self):
        # Since the left and right feed is so long, we do not
        # want it represented in the string.
        return str({"command": self.command})
    

if __name__ == "__main__":
    print(str(camera_feed_data("Test", "Test")))