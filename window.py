from ui_bricks import *
import cv2

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        self.setFixedSize(frame.shape[1], frame.shape[0])
        self.camera = AppCamera(self)
        
        self.info = QFrame(self)
        self.info.setFixedSize(200, 100)
        self.info.setStyleSheet('background-color: #ddd; color: black;')
        self.info.move(20, self.height() - self.info.height() - 20)

        
class AppCamera(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.setStyleSheet('background-color: #eee; color: black;')
        
        self.image = AppImage()
        self.layout_camera = AppStackLayout()
        self.layout_camera.addWidget(self.image)
        self.setLayout(self.layout_camera)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(50)
        self.update_image()

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        
        color = ColorBRG.CYAN
        for x, y, w, h in faces:
            c = (x + w // 2, y + h // 2)
            rect = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            rotated_rect = [self.rotate_point(c, pt, 45) for pt in rect]
            rotated_rect = np.array(rotated_rect, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [rotated_rect], isClosed=True, color=color, thickness=2)
            color = ColorBRG.BLUE

        return frame
    
    def rotate_point(self, center, point, angle):
        angle_rad = np.radians(angle)
        ox, oy = center
        px, py = point
        
        qx = ox + np.cos(angle_rad) * (px - ox) - np.sin(angle_rad) * (py - oy)
        qy = oy + np.sin(angle_rad) * (px - ox) + np.cos(angle_rad) * (py - oy)
        return int(qx), int(qy)
        
    def update_image(self):
        ret, frame = self.parent().cap.read()
        cv2.imwrite("frame.jpg", frame)
        detected_frame = self.detect_faces(frame)
        detected_frame = cv2.flip(detected_frame, 1)
        self.image.setImage(detected_frame)