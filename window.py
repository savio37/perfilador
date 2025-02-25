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
        self.setFixedSize(960, 720)
        
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
        self.focus_name = '???'
        self.detect = 0
        self.small_frame = None
        self.faces = None
        
        self.image = AppImage()
        self.layout_camera = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_camera.setContentsMargins(0, 0, 0, 0)
        self.layout_camera.addWidget(self.image)
        self.setLayout(self.layout_camera)
        
        self.known_encodings = []
        self.known_names = []
        
        for file in os.listdir('img'):
            if file.endswith('.jpg'):
                image = face_recognition.load_image_file(f'img/{file}')
                encoding = face_recognition.face_encodings(image, model='small')[0]
                self.known_encodings.append(encoding)
                self.known_names.append(file.split('.')[0])
                
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(25)
        self.update_image()
        
        self.timer_identify = QTimer(self)
        self.timer_identify.timeout.connect(self.identify_face)
        self.timer_identify.start(1000)
                

    def detect_faces(self, frame):
        self.small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        self.detect -= 1
        if self.detect <= 0:
            self.faces = face_recognition.face_locations(self.small_frame, model='hog')
            self.detect = 3
        
        color = Color.CYAN
        for top, right, bottom, left in self.faces:
            top, right, bottom, left = top * 1.8, right * 2.2, bottom * 2.2, left * 1.8
            face_rect = (top, right, bottom, left)
            Drawing.face_marker(frame, face_rect, color)
            if color == Color.CYAN:
                Drawing.face_name(frame, face_rect, self.focus_name.split(' ')[0])
            
            color = Color.LIGHT_GRAY
        
        face_rect = self.faces[0] if len(self.faces) > 0 else (0, 0, 0, 0)
        face_info = db.get_info(self.focus_name)[0] if self.focus_name != '???' else ('???', 0, '', '')

        return frame, face_rect, face_info
    
    def identify_face(self):
        self.focus_name = "???"
        if len(self.faces) > 0:
            self.face_encoding = face_recognition.face_encodings(self.small_frame, self.faces, model='small')[0]
            face_distances = face_recognition.face_distance(self.known_encodings, self.face_encoding)
            face_distances = list(face_distances)
            if min(face_distances) < 0.6:
                self.focus_name = self.known_names[face_distances.index(min(face_distances))]
        
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
        self.layout_info.addWidget(self.label_profession, 2, 1, 1, 2)
        self.setLayout(self.layout_info)

    def setInfo(self, img: np.ndarray, info:tuple):
        name, age, pronouns, profession = info
        self.image.setImage(img)
        self.label_name.setText(name.split(' ')[0] + ' ' + name.split(' ')[-1][:1] + '.')
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
        