from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from tools import *
import face_recognition

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.setFixedSize(640, 480)
        
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
            face_rect = (top, right, bottom, left)
            Drawing.face_marker(frame, face_rect, color)
            Drawing.face_name(frame, face_rect, 'Unknown')
            
            color = Color.LIGHT_GRAY
            
        return frame, faces[0] if len(faces) > 0 else (0, 0, 0, 0)
        
    def update_image(self):
        ret, frame = self.parent().cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_img = frame.copy()
        cam_img, face_pos = self.detect_faces(frame)
        self.image.setImage(cam_img)
        
        top, right, bottom, left = face_pos
        face_img = face_img[top*2:bottom*2, left*2:right*2].copy()
        self.parent().info_card.setImage(face_img)
        
        
class AppInfoCard(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedSize(200, 70)
        self.setStyleSheet('background-color: #ddd; color: black;')
        
        self.image = AppImage()
        self.image.setFixedSize(50, 50)
        
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