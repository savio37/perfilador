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
        self.setMinimumSize(640, 480)
        
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        
        self.info_card = AppInfoCard(self)
        
        self.camera = AppCamera(self)
        self.layout_content = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_content.setContentsMargins(0, 0, 0, 0)
        self.layout_content.addWidget(self.camera)
        self.setLayout(self.layout_content)
        
        self.info_card = AppInfoCard(self)
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
 
            top, right, bottom, left = top * 0.9, right * 1.1, bottom * 1.1, left * 0.9
            cx, cy = (left + right) // 2, (top + bottom) // 2
            size = 8
            
            points = [(cx - size, top + size), (cx, top), (cx + size, top + size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            
            points = [(right - size, cy - size), (right, cy), (right - size, cy + size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            
            points = [(cx + size, bottom - size), (cx, bottom), (cx - size, bottom - size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            
            points = [(left + size, cy + size), (left, cy), (left + size, cy - size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            color = Color.BLUE

        return frame, faces[0] if len(faces) > 0 else (0, 0, 0, 0)
        
    def update_image(self):
        ret, frame = self.parent().cap.read()
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_img = frame.copy()
        cam_img, rect = self.detect_faces(frame)
        self.image.setImage(cam_img)
        
        top, right, bottom, left = rect
        face_img = face_img[top:bottom, left:right].copy()
        self.parent().info_card.setImage(face_img)
        
        
class AppInfoCard(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedSize(200, 100)
        self.setStyleSheet('background-color: #ddd; color: black;')
        
        self.image = AppImage()
        self.image.setFixedSize(80, 80)
        
        self.layout_info = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_info.setContentsMargins(10, 10, 10, 10)
        self.layout_info.addWidget(self.image)
        self.setLayout(self.layout_info)
        
    def setImage(self, array: np.ndarray):
        self.image.setImage(array)
        
        
class AppImage(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        
    def setImage(self, array: np.ndarray):
        height, width, channel = array.shape
        bytesPerLine = 3 * width
        qImg = QImage(array.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qImg))