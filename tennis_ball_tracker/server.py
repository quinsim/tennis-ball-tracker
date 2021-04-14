# Standard library imports
import logging
import threading

# Third party imports

# Local application imports
from tennis_ball_tracker.CameraFeed import CameraFeed
from tennis_ball_tracker import api
from tennis_ball_tracker import session 
from tennis_ball_tracker import messages


IP_ADDRESS = "127.0.0.1"

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
            api.CMD_STOP_SENDING_CAMERA_FEED: self.stop_sending_camera_feed
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
                        logging.debug("Response sent {response}".format(response=dict(response)))
                        print("Response sent {response}".format(response=dict(response)))
                        self.ctrl_session.send(dict(response))

    def run_camera_feed(self):
        logging.debug("Started the {}".format(threading.current_thread().name))
        print("Started the {}".format(threading.current_thread().name))
        while self.is_connected:
            if self.send_camera_feed:
                left, right = self.camera.getStereoFrames()
                req = messages.camera_feed_data(left, right)
                self.camera_feed_session.send(dict(req))

    def __str__(self):
        return "server"

if __name__ == "__main__":
    import tennis_ball_tracker.config as config
    server_ = server(config.CTRL_PORT, config.CAMERA_FEED_PORT)
    server_.connect(config.IP_ADDRESS)