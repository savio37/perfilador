import numpy as np
import cv2
import sqlite3


class Color:
    CYAN = (0, 255, 255)
    LIGHT_GRAY = (211, 211, 211)
    WHITE = (255, 255, 255)
    
    
class Drawing:
    @staticmethod
    def face_marker(frame:np.ndarray, face_rect:tuple, color:Color=Color.LIGHT_GRAY, size:int=15):
        top, right, bottom, left = face_rect
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
    def face_name(frame:np.ndarray, face_rect:tuple, name:str, color:Color=Color.WHITE):
        top, right, bottom, left = face_rect
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.75
        thickness = 2
        name_size = cv2.getTextSize(name, font, scale, thickness)[0][0]
        name_pos = (int((left + right - name_size) / 2), int(top - 20))
        
        cv2.putText(frame, name, name_pos, font, scale, color, thickness)
        

class SQLiteDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SQLiteDB, cls).__new__(cls)
            cls._instance.conn = None
        return cls._instance

    def connect(self):
        if not self.conn:
            try:
                self.conn = sqlite3.connect("data/database.db")
                self.conn.execute('PRAGMA foreign_keys = ON')
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                
    def execute_query(self, query, values=None):
        try:
            cursor = self.conn.cursor()
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            

class FacadeDB:
    def __init__(self):
        self.db = SQLiteDB()


    def get_info(self, name: str):
        self.db.connect()
        query = "SELECT * FROM identidades WHERE nome = ?"
        result = self.db.execute_query(query, (name,))
        self.db.close()
        return result
    

db = FacadeDB()
