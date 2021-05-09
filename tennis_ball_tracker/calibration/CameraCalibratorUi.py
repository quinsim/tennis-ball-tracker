# Standard library imports
import os
import logging

# Third party imports
import cv2
import remi.gui as gui
import numpy as np
from remi import start, App

# Local application imports
import tennis_ball_tracker.config as config
from tennis_ball_tracker.CameraFeed import CameraFeed
from tennis_ball_tracker.calibration.camera_calibrator import CameraCalibrator
from tennis_ball_tracker.calibration.camera_calibration import calibrate_camera, save_camera_calibration


camera = CameraFeed()

class VideoDisplayWidget(gui.Image):
    """
    Remi widget to visualize a video feed.

    Args:
        camera (CameraFeed): The driver for the camera.
        fps (int): The fps to run video display at.
    """
    # def __init__(self, camera, fps, **kwargs):
    def __init__(self, fps, **kwargs):
        super(VideoDisplayWidget, self).__init__("/%s/get_image_data" % id(self), **kwargs)
        javascript_code = gui.Tag()
        javascript_code.type = 'script'
        javascript_code.attributes['type'] = 'text/javascript'
        javascript_code.add_child('code', """
            function update_image%(id)s(){
                var url = '/%(id)s/get_image_data';
                var xhr = new XMLHttpRequest();
                xhr.open('GET', url, true);
                xhr.responseType = 'blob'
                xhr.onload = function(e){
                    var urlCreator = window.URL || window.webkitURL;
                    var imageUrl = urlCreator.createObjectURL(this.response);
                    document.getElementById('%(id)s').src = imageUrl;
                }
                xhr.send();
            };

            setInterval( update_image%(id)s, %(update_rate)s );
            """ % {'id': id(self), 'update_rate': 1000.0 / fps})

        self.add_child('javascript_code', javascript_code)
        
    def get_image_data(self):
        """
        Get a single frame from the snickerdoodle stereo camera
        and package it up for remi.

        Returns:
            List[str, dict]: [The jpg img string, remi video header]
        """
        headers = {'Content-type': 'image/jpeg'}

        assert isinstance(camera, CameraFeed)
        self.left, self.right = camera.getStereoFrames()
        left_and_right = np.concatenate((self.left.RGB, self.right.RGB), axis=1)
        ret, jpeg = cv2.imencode('.jpg', left_and_right)
        return [jpeg.tostring(), headers]

class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)
        self.calibrator = CameraCalibrator((8, 6))
        self._progress = 0
        self._progress_max = self.calibrator.REQUIRED_NUMBER_OF_IMGS
        
    def main(self, name='world'):  
        verticalContainer = gui.Container(width=1524, margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})
        horizontalContainer = gui.Container(width='100%', layout_orientation=gui.Container.LAYOUT_HORIZONTAL, margin='0px', style={'display': 'block', 'overflow': 'auto'})

        # self.videoDisplay = VideoDisplayWidget(self.camera, 10, width=752*2, height=480)
        self.videoDisplay = VideoDisplayWidget(10, width=752*2, height=480)
        self.videoDisplay.style['margin'] = '10px'
        
        self.capture_btn = gui.Button('Capture', width=200, height=30, margin='10px')
        self.calibrate_btn = gui.Button('Calibrate', width=200, height=30, margin='10px')
        self.close_btn = gui.Button('Close', width=200, height=30, margin='10px')
        self.progress = gui.Progress(self._progress, self._progress_max)

        self.capture_btn.onclick.do(self.capture_img)
        self.calibrate_btn.onclick.do(self.calibrate)
        self.close_btn.onclick.do(self.close)

        horizontalContainer.append(self.videoDisplay)
        verticalContainer.append(self.capture_btn)
        verticalContainer.append(self.calibrate_btn)
        verticalContainer.append(self.close_btn)
        verticalContainer.append(horizontalContainer)
        verticalContainer.append(self.progress)

        return verticalContainer
      
    def capture_img(self, _):
        left = self.videoDisplay.left
        left_greyscale = self.calibrator.to_greyscale(left.RGB)
        
        right = self.videoDisplay.right
        right_greyscale = self.calibrator.to_greyscale(right.RGB)

        err = None
        if self.calibrator.verify_pattern(left_greyscale, self.calibrator.grid_pattern):
            if self.calibrator.verify_pattern(right_greyscale, self.calibrator.grid_pattern):
                self.calibrator.save_calibration_image(self.calibrator.LEFT_PATH, self.calibrator.img_ext, left)
                self.calibrator.save_calibration_image(self.calibrator.RIGHT_PATH, self.calibrator.img_ext, right)
                self._progress += 1
                self.progress.set_value(self._progress)
            else:
                err = "Right img is not valid"
        else:
            err = "Left img is not valid"

    def calibrate(self, _):
        if self._progress >= self._progress_max:
            left_cam = calibrate_camera(
                config.LEFT_CALIBRATION_IMGS,
                self.calibrator.grid_pattern,
            )
            right_cam = calibrate_camera(
                config.RIGHT_CALIBRATION_IMGS,
                self.calibrator.grid_pattern,
            )

            save_camera_calibration(
                config.CALIBRATION_CONFIG,
                left_cam,
                right_cam,
            )            
        
    def on_close(self):
        print("closing server")
        super(MyApp, self).on_close()

    #this is required to override the BaseHTTPRequestHandler logger
    def log_message(self, *args, **kwargs):
        pass
        
if __name__ == "__main__":
    logging.getLogger('remi').setLevel(logging.WARNING)
    logging.getLogger('remi').disabled = True
    logging.getLogger('remi.server.ws').disabled = True
    logging.getLogger('remi.server').disabled = True
    logging.getLogger('remi.request').disabled = True
    start(MyApp, debug=False, address='0.0.0.0', port=8081, start_browser=False, multiple_instance=False)