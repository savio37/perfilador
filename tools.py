import numpy as np
import cv2


class Color:
    CYAN = (0, 255, 255)
    LIGHT_GRAY = (211, 211, 211)
    WHITE = (255, 255, 255)
    
    
class Geometry:
    @staticmethod
    def draw_face_marker(frame:np.ndarray, top:int, right:int, bottom:int, left:int, color:Color=Color.LIGHT_GRAY, size:int=15):
        cx, cy = (left + right) // 2, (top + bottom) // 2
        
        points = [(cx - size, top + size), (cx, top), (cx + size, top + size)]
        points = np.array(points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
        
        points = [(cx + size, bottom - size), (cx, bottom), (cx - size, bottom - size)]
        points = np.array(points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
        
        points = [(left + size, cy + size), (left, cy), (left + size, cy - size)]
        points = np.array(points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
        
        points = [(right - size, cy - size), (right, cy), (right - size, cy + size)]
        points = np.array(points, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [points], isClosed=False, color=color, thickness=2)
        
        
    @staticmethod
    def draw_face_name(frame:np.ndarray, top:int, right:int, bottom:int, left:int, name:str, color:Color=Color.WHITE):
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.75
        thickness = 2
        name_size = cv2.getTextSize(name, font, scale, thickness)[0][0]
        name_pos = (int((left + right - name_size) / 2), int(top - 20))
        
        cv2.putText(frame, name, name_pos, font, scale, color, thickness)
