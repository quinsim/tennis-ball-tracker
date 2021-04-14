# Standard library imports
import os
import cv2
import ctypes

# Third party imports
import numpy as np

# Local application imports

DOT_SO_PATH = "/fusion2/camera_feed.so"
# DOT_SO_PATH = "/fusion2/imageFeedthroughDriver.so"

class Frame(object):
    """
    Defines a Frame.

    Args:
        data (): The stereo data.

    Attributes:
        ALL (): All the stereo data.
        RGB (): the rgb stereo data.
        RED (): the red stereo data.
        GREEN (): the green stereo data.
        BLUE (): the blue stereo data.
        GREYSCALE (): the greyscale stereo data.
    """
    def __init__(self, data):
        self.ALL = data
        self.RGB = data[:,:,:3]
        self.GREYSCALE = data[:,:,3]
        # Clear the Red and Green
        b = self.RGB.copy()
        b[:,:,1:] = 0
        self.BLUE = b
        # Clear the Red and Blue
        g = self.RGB.copy()
        g[:,:,0] = g[:,:,2] = 0
        self.GREEN = g
        # Clear the Blue and Green
        r = self.RGB.copy()
        r[:,:,:2] = 0
        self.RED = r

class CameraFeed(object):
    """
    Module to assist with getting the raw feed from the snickerdoodle's
    left and right camera.
    """
    
    def __init__(self):
        self.dll = ctypes.cdll.LoadLibrary(DOT_SO_PATH)
        self.dll.init()
        self.blank_stereo_data = np.ones((480, 752, 8), dtype=np.uint8)
    
    def getStereoFrames(self):
        """
        Gets the stereo frame of the left and right camera.

        Returns:
            Tuple[Frame, Frame]: (the left frame, the right frame)
        """
        stereo_data = self.blank_stereo_data.copy()
        self.dll.getFrame(ctypes.c_void_p(stereo_data.ctypes.data))
        return Frame(stereo_data[:,:,:4]), Frame(stereo_data[:,:,4:])

    def getStereoAll(self):
        """
        Gets the stereo frame for the left and right camera.

        Returns:
            Tuple[]: (the left frame, the right frame)
        """
        left, right = self.getStereoFrames()
        return left.ALL, right.ALL

    def getStereoRGB(self):
        """
        Gets the RGB stereo data for the left and right camera.

        Returns:
            Tuple[]: (the left RGB frame, the right RGB frame)
        """
        left, right = self.getStereoFrames()
        return left.RGB, right.RGB

    def getStereoRed(self):
        """
        Gets the red stereo data for the left and right camera.

        Returns:
            Tuple[]: (the left red frame, the right red frame)
        """
        left, right = self.getStereoFrames()
        return left.RED, right.RED
    
    def getStereoGreen(self):
        """
        Gets the green stereo data for the left and right camera.

        Returns:
            Tuple[]: (the left green frame, the right green frame)
        """
        left, right = self.getStereoFrames()
        return left.GREEN, right.GREEN
    
    def getStereoBlue(self):
        """
        Gets the blue stereo data for the left and right camera.

        Returns:
            Tuple[]: (the left blue frame, the right blue frame)
        """
        left, right = self.getStereoFrames()
        return left.BLUE, right.BLUE

    def getStereoGrey(self):
        """
        Gets the grey stereo frame for the left and right camera.

        Returns:
            Tuple[]: (the left Grey frame, the right Grey frame)
        """
        left, right = self.getStereoFrames()
        return left.GREYSCALE, right.GREYSCALE

    def saveStereoFrame(self, filepath, frame):
        """
        Save the given stereo frame to a file.

        Args:
            filepath (str): The path the file will be saved to.
            data (): The stereo data.
        """
        cv2.imwrite(filepath, frame)
    
    def saveStereoAll(self, filepath):
        """
        Save the stereo frame of the left and right camera to files.
        
        filepath example: ``/tmp/stereo_all.bmp``

        Args:
            filepath (str): The path the file will be saved to.
        """
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        left = "left_{}".format(basename)
        right = "right_{}".format(basename)

        left_frame, right_frame = self.getStereoAll()
        self.saveStereoFrame(os.path.join(dirname, left), left_frame)
        self.saveStereoFrame(os.path.join(dirname, right), right_frame)

    def saveStereoRGB(self, filepath):
        """
        Save the RGB stereo frame of the left and right camera to files.

        filepath example: ``/tmp/stereo_all.bmp``
        
        Args:
            filepath (str): The path the file will be saved to.
        """
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        left = "left_{}".format(basename)
        right = "right_{}".format(basename)

        left_frame, right_frame = self.getStereoRGB()
        self.saveStereoFrame(os.path.join(dirname, left), left_frame)
        self.saveStereoFrame(os.path.join(dirname, right), right_frame)

    def saveStereoRed(self, filepath):
        """
        Save the RGB stereo frame of the left and right camera to files.

        filepath example: ``/tmp/stereo_all.bmp``
        
        Args:
            filepath (str): The path the file will be saved to.
        """
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        left = "left_{}".format(basename)
        right = "right_{}".format(basename)

        left_frame, right_frame = self.getStereoRed()
        self.saveStereoFrame(os.path.join(dirname, left), left_frame)
        self.saveStereoFrame(os.path.join(dirname, right), right_frame)
    
    def saveStereoGreen(self, filepath):
        """
        Save the green stereo frame of the left and right camera to files.

        filepath example: ``/tmp/stereo_all.bmp``
        
        Args:
            filepath (str): The path the file will be saved to.
        """
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        left = "left_{}".format(basename)
        right = "right_{}".format(basename)

        left_frame, right_frame = self.getStereoGreen()
        self.saveStereoFrame(os.path.join(dirname, left), left_frame)
        self.saveStereoFrame(os.path.join(dirname, right), right_frame)
    
    def saveStereoBlue(self, filepath):
        """
        Save the blue stereo frame of the left and right camera to files.

        filepath example: ``/tmp/stereo_all.bmp``
        
        Args:
            filepath (str): The path the file will be saved to.
        """
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        left = "left_{}".format(basename)
        right = "right_{}".format(basename)

        left_frame, right_frame = self.getStereoBlue()
        self.saveStereoFrame(os.path.join(dirname, left), left_frame)
        self.saveStereoFrame(os.path.join(dirname, right), right_frame)
    
    def saveStereoGrey(self, filepath):
        """
        Save the grey stereo frame of the left and right camera to files.

        filepath example: ``/tmp/stereo_all.bmp``
        
        Args:
            filepath (str): The path the file will be saved to.
        """
        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        left = "left_{}".format(basename)
        right = "right_{}".format(basename)

        left_frame, right_frame = self.getStereoGrey()
        self.saveStereoFrame(os.path.join(dirname, left), left_frame)
        self.saveStereoFrame(os.path.join(dirname, right), right_frame)

    def __del__(self):
        self.dll.destroy


if __name__ == "__main__":
    import datetime
    import threading 
    
    # def test_frames_per_second(number_of_threads, number_of_frames):
    #     camera = CameraFeed()
    #     now = datetime.datetime.now()
    #     for _ in range(int(number_of_frames/number_of_threads)):
    #         threads = []
    #         for _ in range(number_of_threads):
    #             thread = threading.Thread(target=camera.getStereoFrames)
    #             thread.start()
    #             threads.append(thread)
    #         [t.join() for t in threads]
    #     total_time = datetime.datetime.now() - now
    #     frames_per_second = number_of_frames / total_time.total_seconds()
    #     del camera
    #     return frames_per_second

    def test_frames_per_second(number_of_frames):

        camera = CameraFeed()
        import datetime
        now = datetime.datetime.now()
        for _ in range(number_of_frames):
            camera.getStereoFrames()
        total_time = datetime.datetime.now() - now
        frames_per_second = number_of_frames / total_time.total_seconds()
        del camera
        return frames_per_second

    fps = test_frames_per_second(100)
    print("FPS {}".format(fps))