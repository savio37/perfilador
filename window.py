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
        self.setFixedSize(480, 640)
        
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
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        faces = face_recognition.face_locations(small_frame, model='hog')
        
        color = Color.CYAN
        for top, right, bottom, left in faces:
 
            top, right, bottom, left = top * 1.8, right * 2.2, bottom * 2.2, left * 1.8
            cx, cy = (left + right) // 2, (top + bottom) // 2
            marker_size = 15
            
            points = [(cx - marker_size, top + marker_size), (cx, top), (cx + marker_size, top + marker_size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            
            points = [(right - marker_size, cy - marker_size), (right, cy), (right - marker_size, cy + marker_size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            
            points = [(cx + marker_size, bottom - marker_size), (cx, bottom), (cx - marker_size, bottom - marker_size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            
            points = [(left + marker_size, cy + marker_size), (left, cy), (left + marker_size, cy - marker_size)]
            points = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
            color = Color.BLUE
            
            name = f'Unknown'
            name_pos = (int(cx - len(name) * 7.5), int(top - 20))
            cv2.putText(frame, name, name_pos, cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.75, color=Color.WHITE, thickness=2)

        return frame, faces[0] if len(faces) > 0 else (0, 0, 0, 0)
        
    def update_image(self):
        ret, frame = self.parent().cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        face_img = frame.copy()
        cam_img, face_pos = self.detect_faces(frame)
        self.image.setImage(cam_img)
        
        top, right, bottom, left = face_pos
        face_img = face_img[top*2:bottom*2, left*2:right*2].copy()
        self.parent().info_card.setImage(face_img)
        
        
class AppInfoCard(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedSize(self.parent().width() - 40, 100)
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