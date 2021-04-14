# Standard library imports

# Third party imports

# Local application imports
from tennis_ball_tracker import api
from tennis_ball_tracker import session 
from tennis_ball_tracker import messages

class client(object):

    def __init__(self, ctrl_port, camera_feed_port):
        self.is_connected = False
        self.ctrl_session = session.zmq_request_session_t(ctrl_port)
        self.camera_feed_session = session.zmq_pull_session_t(camera_feed_port)
    
    def connect(self, ip_address):
        if not self.is_connected:
            self.ctrl_session.start(ip_address)
            self.camera_feed_session.start(ip_address)
            self.is_connected = True
    
    def disconnect(self):
        if self.is_connected:
            self.ctrl_session.stop()
            self.camera_feed_session.stop()
    
    def start_tracking_tennisball(self):
        msg_handler = messages.start_tracking_req
        msg_handler_response = messages.status_rep

        req = msg_handler()
        reply = self.ctrl_session.send_receive(dict(req), block=True)
        
        msg = msg_handler_response(**reply)
        assert (msg.successful == True), msg.msg
    
    def stop_tracking_tennisball(self):
        msg_handler = messages.stop_tracking_req
        msg_handler_response = messages.status_rep

        req = msg_handler()
        reply = self.ctrl_session.send_receive(dict(req), block=True)
        
        msg = msg_handler_response(**reply)
        assert (msg.successful == True), msg.msg

    def calibrate_camera(self):
        msg_handler = messages.calibrate_camera_req
        msg_handler_response = messages.status_rep

        req = msg_handler()
        reply = self.ctrl_session.send_receive(dict(req), block=True)
        
        msg = msg_handler_response(**reply)
        assert (msg.successful == True), msg.msg

    def blink_led(self, period_ms, duty_cycle_percent):
        msg_handler = messages.configure_led_req
        msg_handler_response = messages.status_rep

        req = msg_handler(period_ms, duty_cycle_percent)
        reply = self.ctrl_session.send_receive(dict(req), block=True)
        
        msg = msg_handler_response(**reply)
        assert (msg.successful == True), msg.msg

    # Debug commands

    def start_sending_camera_feed(self):
        msg_handler = messages.start_sending_camera_feed_req
        msg_handler_response = messages.status_rep

        req = msg_handler()
        reply = self.ctrl_session.send_receive(dict(req), block=True)
        
        msg = msg_handler_response(**reply)
        assert (msg.successful == True), msg.msg

    def stop_sending_camera_feed(self):
        msg_handler = messages.stop_sending_camera_feed_req
        msg_handler_response = messages.status_rep

        req = msg_handler()
        reply = self.ctrl_session.send_receive(dict(req), block=True)
        
        msg = msg_handler_response(**reply)
        assert (msg.successful == True), msg.msg

    def process_camera_feed(self):
        msg_handler = messages.camera_feed_data

        reply = self.camera_feed_session.receive(True)
        msg = msg_handler(**reply)
        return msg

if __name__ == "__main__":
    import tennis_ball_tracker.config as config
    client_ = client(config.CTRL_PORT, config.CAMERA_FEED_PORT)
    client_.connect(config.IP_ADDRESS)
    client_.calibrate_camera()

    client_.start_sending_camera_feed()
    
    import datetime
    number_of_frames = 100
    now = datetime.datetime.now()
    for _ in range(number_of_frames):
        client_.process_camera_feed()
    total_time = datetime.datetime.now() - now
    fps = number_of_frames / total_time
    print("FPS {}".format(fps))

    client_.stop_tracking_tennisball()
    client_.disconnect()