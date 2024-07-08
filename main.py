import sys
from PyQt6.QtWidgets import QApplication  
from window import AppWindow
          
app = QApplication(sys.argv)
root = AppWindow()
root.show()
sys.exit(app.exec())