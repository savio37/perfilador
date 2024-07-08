from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import numpy as np


class AppStackLayout(QBoxLayout):
    def __init__(self):
        super().__init__(QBoxLayout.Direction.TopToBottom)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        
        
class AppImage(QLabel):
    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        
    def setImage(self, array: np.ndarray):
        height, width, channel = array.shape
        bytesPerLine = 3 * width
        qImg = QImage(array.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
        self.setPixmap(QPixmap.fromImage(qImg))