from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from tools import *
import face_recognition
import os

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        
        self.info_card = AppInfoCard(self)
        
        self.camera = AppCamera(self)
        self.layout_content = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_content.setContentsMargins(0, 0, 0, 0)
        self.layout_content.addWidget(self.camera)
        self.setLayout(self.layout_content)
        
        self.info_card = AppInfoCard(self)
        self.info_card.move(int((self.width() - self.info_card.width())/2), self.height() - self.info_card.height() - 20)

        
class AppCamera(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.image = AppImage()
        self.layout_camera = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_camera.setContentsMargins(0, 0, 0, 0)
        self.layout_camera.addWidget(self.image)
        self.setLayout(self.layout_camera)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(50)
        self.update_image()
        
        self.known_encodings = []
        self.known_names = []
        
        for file in os.listdir('img'):
            if file.endswith('.png'):
                image = face_recognition.load_image_file(f'img/{file}')
                encoding = face_recognition.face_encodings(image)[0]
                self.known_encodings.append(encoding)
                self.known_names.append(file.split('.')[0])
                

    def detect_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        faces = face_recognition.face_locations(small_frame, model='hog')
        
        name = "???"
        if len(faces) > 0:
            face_encoding = face_recognition.face_encodings(small_frame, [faces[0]], model='small')[0]
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            face_distances = list(face_distances)
            if min(face_distances) < 0.6:
                name = self.known_names[face_distances.index(min(face_distances))]
        
        color = Color.CYAN
        for top, right, bottom, left in faces:
            top, right, bottom, left = top * 1.8, right * 2.2, bottom * 2.2, left * 1.8
            face_rect = (top, right, bottom, left)
            Drawing.face_marker(frame, face_rect, color)
            if color == Color.CYAN:
                Drawing.face_name(frame, face_rect, name.split(' ')[0])
            
            color = Color.LIGHT_GRAY
        
        face_rect = faces[0] if len(faces) > 0 else (0, 0, 0, 0)
        face_info = db.get_info(name)[0] if name != '???' else ('???', 0, '', '')
            
        return frame, face_rect, face_info
        
    def update_image(self):
        ret, frame = self.parent().cap.read()
        #frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_img = frame.copy()
        cam_img, face_rect, face_info = self.detect_faces(frame)
        self.image.setImage(cam_img)
        
        top, right, bottom, left = face_rect
        face_img = face_img[top*2:bottom*2, left*2:right*2].copy()
        self.parent().info_card.setInfo(face_img, face_info)
        
        
class AppInfoCard(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setFixedSize(300, 100)
        self.setStyleSheet('border-radius:5px; background-color: #111; color: white; font-family: Lexend; font-size: 16px;')
        
        self.image = AppImage()
        self.image.setFixedSize(80, 80)
        
        self.label_name = QLabel('???')
        self.label_name.setStyleSheet('font-size: 18px; font-weight: bold;')
        self.label_pronouns = QLabel('')
        self.label_pronouns.setStyleSheet('font-size: 14px;')
        self.label_age = QLabel('')
        self.label_profession = QLabel('')
        
        self.layout_info = QGridLayout()
        self.layout_info.setContentsMargins(10, 10, 10, 10)
        self.layout_info.addWidget(self.image, 0, 0, 3, 1)
        self.layout_info.addWidget(self.label_name, 0, 1, 1, 1)
        self.layout_info.addWidget(self.label_pronouns, 0, 2, 1, 1)
        self.layout_info.addWidget(self.label_age, 1, 1, 1, 1)
        self.layout_info.addWidget(self.label_profession, 2, 1, 1, 1)
        self.setLayout(self.layout_info)

    def setInfo(self, img: np.ndarray, info:tuple):
        name, age, pronouns, profession = info
        self.image.setImage(img)
        self.label_name.setText(name)
        self.label_age.setText(f'{age} anos')
        self.label_pronouns.setText(pronouns)
        self.label_profession.setText(profession)
        self.hide() if name == '???' else self.show()
        
        
class AppImage(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        
    def setImage(self, array: np.ndarray):
        height, width, channel = array.shape
        bytesPerLine = 3 * width
        qImg = QImage(array.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qImg))