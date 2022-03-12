import cv2 as cv
import threading
import numpy as np

class CSI_Camera:
    def __init__(self, sensor_id):
        self.capture = None
        self.frame = None
        self.grabbed = None
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False
        self.id = sensor_id

    def open(self):
        gstmr = self.gstreamerPipeline(self.id)
        try:
            self.capture = cv.VideoCapture(gstmr, cv.CAP_GSTREAMER)
            self.grabbed, self.frame = self.capture.read()
        except RuntimeError:
            self.capture = None
            print("Error: Unable to open camera.")
            print("Pipeline:", gstmr)
    def start(self):
        if self.running:
            print("Camera already running")
            return None
        if self.capture != None:
            # Create Thread to read frames
            self.running = True
            self.read_thread = threading.Thread(target=self.update)
            self.read_thread.start()
        return self
    def stop(self):
        self.running = False
        # Kill Thread
        self.read_thread.join()
        self.read_thread = None
    def update(self):
        while self.running:
            try:
                grabbed, frame = self.capture.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            except RuntimeError:
                print("Error: Could not read image from camera.")
    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame
    def release(self):
        if self.capture != None:
            self.capture.release()
            self.capture = None
        if self.read_thread != None:
            self.read_thread.join()
    def isRunning(self):
        return self.running
    def isOpened(self):
        if self.capture != None:
            return self.capture.isOpened()
        else:
            return False
    def gstreamerPipeline(self, sensor_id, cap_width=1280, cap_height=720, disp_width=1280, disp_height=720, framerate=30, flip=0):
        return (
            "nvarguscamerasrc sensor-id=%d ! "
            "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                sensor_id,
                cap_width,
                cap_height,
                framerate,
                flip,
                disp_width,
                disp_height,
            )
        )