from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from tools import *
import numpy as np
import cv2
import face_recognition

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        self.setFixedSize(frame.shape[1], frame.shape[0])
        self.camera = AppCamera(self)
        
        self.info_card = QFrame(self)
        self.info_card.setFixedSize(200, 100)
        self.info_card.setStyleSheet('background-color: #ddd; color: black;')
        self.info_card.move(20, self.height() - self.info_card.height() - 20)

        
class AppCamera(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setStyleSheet('background-color: #eee; color: black;')
        
        self.image = AppImage()
        self.layout_camera = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_camera.setContentsMargins(0, 0, 0, 0)
        self.layout_camera.addWidget(self.image)
        self.setLayout(self.layout_camera)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(50)
        self.update_image()

    def detect_faces(self, frame):
        faces = face_recognition.face_locations(frame, model='hog')
        
        color = Color.CYAN
        for top, right, bottom, left in faces:
            cx, cy = (left + right) // 2, (top + bottom) // 2
            points = [(cx, top), (right, cy), (cx, bottom), (left, cy)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=True, color=color, thickness=2)
            color = Color.BLUE

        return frame
        
    def update_image(self):
        ret, frame = self.parent().cap.read()
        detected_frame = self.detect_faces(frame)
        #detected_frame = cv2.flip(detected_frame, 1)
        self.image.setImage(detected_frame)
        
        
class AppImage(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        
    def setImage(self, array: np.ndarray):
        height, width, channel = array.shape
        bytesPerLine = 3 * width
        qImg = QImage(array.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
        self.setPixmap(QPixmap.fromImage(qImg))