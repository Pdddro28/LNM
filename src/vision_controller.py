import cv2
import numpy as np
from dataclasses import dataclass
from picamera2 import Picamera2  
import time

# --- DATA STRUCTURES ---
@dataclass
class ROI:
    x1: int; y1: int
    x2: int; y2: int

# --- VISION SYSTEM CONTROLLER ---
class VisionController():
    
    # --- INITIALIZATION AND CAMERA SETUP ---
    def __init__(self):
        self.image_width  = 640 
        self.image_height = 370 
        self.image_lab = 0
        self.frame = None

        # Variables para la detección de atasco visual
        self.prev_gray_frame = None
        self.ultima_vez_con_movimiento = time.time()
        self.UMBRAL_CAMBIO_PIXELS = 150000  # Ajustar sensibilidad según pruebas
        self.TIEMPO_MAXIMO_ESTATICO = 5  # Segundos permitidos antes del freno

        self.camera = Picamera2()
        self.camera.resolution = (self.image_width, self.image_height)
        self.camera.framerate = 32
        config = self.camera.create_video_configuration(main={"format": 'RGB888', 'size': (self.image_width, self.image_height)})
        self.camera.configure(config)
        self.camera.start()
        
        time.sleep(0.1)

    # --- IMAGE ACQUISITION AND PROCESSING ---
    def receive_image(self):
        self.frame = self.camera.capture_array('main')
        self.frame = cv2.flip(self.frame, 0)
        self.frame = cv2.flip(self.frame, 1)

        if self.frame is None:
            print("No se pudo obtener imagen de la PiCamera.")
            return

        self.image_lab = cv2.cvtColor(self.frame, cv2.COLOR_BGR2LAB)
        
        l_channel, a_channel, b_channel = cv2.split(self.image_lab)
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl_channel = clahe.apply(l_channel)
        
        self.image_lab = cv2.merge((cl_channel, a_channel, b_channel))
        
        self.image_lab = cv2.GaussianBlur(self.image_lab, (7, 7), 0)

    # --- ANTI-STUCK DETECTION ALGORITHM ---
    def check_if_stuck(self) -> bool:
        """
        Compara el frame actual con el anterior. 
        Retorna True si el carro lleva atrapado más del tiempo permitido.
        """
        if self.frame is None:
            return False

        # Convertir frame actual a escala de grises
        current_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # Si es la primera vuelta, inicializamos el frame previo y salimos
        if self.prev_gray_frame is None:
            self.prev_gray_frame = current_gray
            self.ultima_vez_con_movimiento = time.time()
            return False

        # Calcular diferencia absoluta y binarizar para remover ruido del sensor
        frame_diff = cv2.absdiff(current_gray, self.prev_gray_frame)
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Contar píxeles que cambiaron de posición
        pixels_cambiados = np.sum(thresh == 255)
        tiempo_actual = time.time()

        # Opcional: Descomentar para calibración en telemetría por consola
        # print(f"Píxeles en movimiento: {pixels_cambiados} | Tiempo estático: {round(tiempo_actual - self.ultima_vez_con_movimiento, 2)}s", end='\r')

        # Si el cambio supera el umbral, el entorno se está moviendo (el carro avanza)
        if pixels_cambiados > self.UMBRAL_CAMBIO_PIXELS:
            self.ultima_vez_con_movimiento = tiempo_actual
            is_stuck = False
        else:
            # Si el tiempo sin detectar cambios supera el límite estipulado
            if (tiempo_actual - self.ultima_vez_con_movimiento) > self.TIEMPO_MAXIMO_ESTATICO:
                is_stuck = True
            else:
                is_stuck = False

        # Guardar el frame actual como el previo para la siguiente ejecución del bucle
        self.prev_gray_frame = current_gray
        return is_stuck

    def reset_stuck_timer(self):
        """Reinicia el temporizador de atasco (útil llamar esto justo después de que el robot se detenga voluntariamente)"""
        self.ultima_vez_con_movimiento = time.time()
        self.prev_gray_frame = None

    # --- DRAWING UTILITIES ---
    def draw_roi(self, roi, color=(0, 255, 0)):
        cv2.rectangle(self.frame, (roi.x1, roi.y1), (roi.x2, roi.y2), color, 2)

    def draw_contours(self, cnt, roi, color):
        cv2.drawContours(self.frame[roi.y1:roi.y2, roi.x1:roi.x2], cnt, -1, color, 2)

    def draw_centroid_line(self, max_contour_data, roi: ROI, color=(255, 0, 0), thickness=2):
        max_cnt = max_contour_data[3]
        if max_cnt is None:
            return None

        M = cv2.moments(max_cnt)
        if M["m00"] != 0:
            global_cx = int(M["m10"] / M["m00"]) + roi.x1
            cv2.line(self.frame, (global_cx, roi.y1), (global_cx, roi.y2), color, thickness)
            
            global_cy = int(M["m01"] / M["m00"]) + roi.y1
            cv2.circle(self.frame, (global_cx, global_cy), 5, color, -1)
            return (global_cx, global_cy)
        else:
            return None

    def draw_parallel_lane_line(self, centroid_coords, roi: ROI, offset=80, avoid_right=True, color=(0, 255, 255), thickness=2):
        if centroid_coords is None:
            return None

        global_cx, global_cy = centroid_coords

        if avoid_right:
            lane_x = global_cx + offset
        else:
            lane_x = global_cx - offset

        lane_x = max(0, min(lane_x, self.image_width))
        cv2.line(self.frame, (lane_x, roi.y1), (lane_x, roi.y2), color, thickness)
        
        arrow_direction = 30 if avoid_right else -30
        cv2.arrowedLine(self.frame, (global_cx, global_cy), (global_cx + arrow_direction, global_cy), color, 2, tipLength=0.3)

        return lane_x

    # --- COMPUTER VISION ALGORITHMS ---
    def find_contours(self, range_colors, roi: ROI):
        img_segmented = self.image_lab[roi.y1:roi.y2, roi.x1:roi.x2]
        lower_mask = np.array(range_colors[0])
        upper_mask = np.array(range_colors[1])
        mask = cv2.inRange(img_segmented, lower_mask, upper_mask)
        
        kernel = np.ones((5, 5), np.uint8)
        smoothed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        smoothed_mask = cv2.morphologyEx(smoothed_mask, cv2.MORPH_OPEN, kernel)
        
        contours = cv2.findContours(smoothed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        return contours
    
    def max_contour(self, contours, roi: ROI):
        max_area = 0
        max_y = 0
        max_x = 0
        max_cnt = None

        for c in contours:
            area = cv2.contourArea(c)
            if area > 100:
                approx = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)
                x, y, w, h = cv2.boundingRect(approx)
                x += roi.x1 + w // 2
                y += roi.y1 + h // 2

                if area > max_area:
                    max_area = area
                    max_y = y
                    max_x = x
                    max_cnt = c

        return [max_area, max_x, max_y, max_cnt]


if "__main__" == __name__:
    pass
