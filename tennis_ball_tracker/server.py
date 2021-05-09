# Standard library imports
import cv2
import json
import base64
import logging
import datetime
import threading
# Third party imports

# Local application imports
import tennis_ball_tracker.config as config
from tennis_ball_tracker import api
from tennis_ball_tracker import session 
from tennis_ball_tracker import messages
from tennis_ball_tracker.CameraFeed import CameraFeed
from tennis_ball_tracker.calibration import camera_calibration
class server(object):

    def __init__(self, ctrl_port, camera_feed_port):
        self.camera = None
        self.is_connected = False
        self.send_camera_feed = False
        
        self.ctrl_session = session.zmq_reply_session_t(ctrl_port)
        self.camera_feed_session = session.zmq_push_session_t(camera_feed_port)
        
        ctrl_worker = threading.Thread(target=self.run, name=str(self) + "_ctrl_thread")
        camera_feed_worker = threading.Thread(target=self.run_camera_feed, name=str(self) + "_camera_feed_thread")
        self.workers = [ctrl_worker, camera_feed_worker]
    
        self.message_handler = {
            api.CMD_START_TRACKING_TENNISBALL: self.start_tracking_tennisball,
            api.CMD_STOP_TRACKING_TENNISBALL: self.stop_tracking_tennisball,
            api.CMD_CALIBRATE_CAMERA: self.calibrate_camera,
            api.CMD_CONFIGURE_LED: self.blink_led,
            # Debug message handlers
            api.CMD_START_SENDING_CAMERA_FEED: self.start_sending_camera_feed,
            api.CMD_STOP_SENDING_CAMERA_FEED: self.stop_sending_camera_feed,
            api.CMD_GET_CAMERA_FEED: self.get_camera_feed,
            api.CMD_TEST_CAMERA_FPS_REQ: self.test_camera_fps,
        }
    
    def connect(self, ip_address):
        if not self.is_connected:
            self.is_connected = True
            self.camera = CameraFeed()

            self.ctrl_session.start(ip_address)
            self.camera_feed_session.start(ip_address)
            [worker.start() for worker in self.workers]
            
    def disconnect(self):
        if self.is_connected:
            self.is_connected = False
            
            [worker.join() for worker in self.workers]
            self.ctrl_session.stop()
            self.camera_feed_session.stop()
            
            del self.camera

    def start_tracking_tennisball(self, reply):
        result = True
        msg = ""
        
        msg_handler = messages.start_tracking_req(**reply)

        return messages.status_rep(msg_handler.command, result, msg)
    
    def stop_tracking_tennisball(self, reply):
        result = True
        msg = ""
        
        msg_handler = messages.stop_tracking_req(**reply)

        return messages.status_rep(msg_handler.command, result, msg)

    def calibrate_camera(self, reply):
        result = True
        msg = ""
        
        msg_handler = messages.calibrate_camera_req(**reply)

        if result:
            try:
                left_cam = camera_calibration.calibrate_camera(
                    config.LEFT_CALIBRATION_IMGS,
                    tuple(config.CALIBRATION_GRID_PTRN),
                )
            except Exception as e:
                msg+= = "Failed to calibrate the left camera!\n" + str(e)
                result = False

        if result:
            try:
                right_cam = camera_calibration.calibrate_camera(
                    config.RIGHT_CALIBRATION_IMGS,
                    tuple(config.CALIBRATION_GRID_PTRN),
                )
            except Exception as e:
                msg+= = "Failed to calibrate the right camera!\n" + str(e)
                result = False

        if result:
            try:
                camera_calibration.save_camera_calibration(
                    config.CALIBRATION_CONFIG,
                    left_cam,
                    right_cam,
                )
            except Exception as e:
                msg+= = "Failed to save the calibrate data!\n" + str(e)
                result = False

        return messages.status_rep(msg_handler.command, result, msg)
        
    def blink_led(self, reply):
        result = True
        msg = ""
        
        msg_handler = messages.configure_led_req(**reply)

        return messages.status_rep(msg_handler.command, result, msg)

    # Debug commands handlers
    
    def start_sending_camera_feed(self, reply):
        result = True
        msg = ""

        msg_handler = messages.start_sending_camera_feed_req(**reply)
        if not self.send_camera_feed:
            self.send_camera_feed = True        
        else:
            result = False
            msg = "Camera Feed is already running"

        return messages.status_rep(msg_handler.command, result, msg)
    
    def stop_sending_camera_feed(self, reply):
        result = True
        msg = ""
        
        msg_handler = messages.stop_sending_camera_feed_req(**reply)
        if self.send_camera_feed:
            self.send_camera_feed = False
        else:
            result = False
            msg = "Camera Feed is not currently running"

        return messages.status_rep(msg_handler.command, result, msg)

    def get_camera_feed(self, reply):
        msg_handler = messages.test_camera_fps_req(**reply)

        left, right = self.camera.getStereoFrames()
        left_str = base64.b64encode(cv2.imencode('.jpg', left.ALL)[1]).decode()
        right_str = base64.b64encode(cv2.imencode('.jpg', right.ALL)[1]).decode()

        return messages.camera_feed_data(left_str, right_str)

    def test_camera_fps(self, reply):
        msg_handler = messages.stop_sending_camera_feed_req(**reply)

        now = datetime.datetime.now()
        number_of_frames = 100
        for _ in range(number_of_frames):
            self.camera.getStereoFrames()
        total_time = datetime.datetime.now() - now
        fps = number_of_frames / total_time.total_seconds()

        return messages.test_camera_fps_rep(fps)

    def run(self):
        logging.debug("Started the {}".format(threading.current_thread().name))
        print("Started the {}".format(threading.current_thread().name))
        while self.is_connected:
            try:
                reply = self.ctrl_session.receive()
            except:
                pass
            else:
                if reply is not None:
                    handler = self.message_handler[reply[api.COMMAND]]
                    logging.debug("Request received {request}".format(request=reply))
                    print("Request received {request}".format(request=reply))
                    response = handler(reply)
                    if response is not None:
                        logging.debug("Response sent {response}".format(response=response))
                        print("Response sent {response}".format(response=response))
                        self.ctrl_session.send(dict(response))
        logging.debug("Stopping the {}".format(threading.current_thread().name))
        print("Stopping the {}".format(threading.current_thread().name))

    def run_camera_feed(self):
        logging.debug("Started the {}".format(threading.current_thread().name))
        print("Started the {}".format(threading.current_thread().name))
        while self.is_connected:
            if self.send_camera_feed:
                left, right = self.camera.getStereoFrames()
                left_str = base64.b64encode(cv2.imencode('.jpg', left.ALL)[1]).decode()
                right_str = base64.b64encode(cv2.imencode('.jpg', right.ALL)[1]).decode()
                req = messages.camera_feed_data(left_str, right_str)
                self.camera_feed_session.send(dict(req))
        logging.debug("Stopping the {}".format(threading.current_thread().name))
        print("Stopping the {}".format(threading.current_thread().name))

    def __str__(self):
        return "server"

if __name__ == "__main__":
    try:
        import tennis_ball_tracker.config as config
        server_ = server(config.CTRL_PORT, config.CAMERA_FEED_PORT)
        server_.connect(config.IP_ADDRESS)
        while True:
            pass
    except KeyboardInterrupt:
        print("Disconnecting from")
        server_.disconnect()