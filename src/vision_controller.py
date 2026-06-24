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
        self.image_width  = 640 #640
        self.image_height = 370 #370
        self.image_lab = 0
        self.frame = None

        self.camera = Picamera2()
        self.camera.resolution = (self.image_width, self.image_height)
        self.camera.framerate = 32
        config = self.camera.create_video_configuration(main={"format": 'RGB888', 'size': (self.image_width, self.image_height)})
        self.camera.configure(config)
        self.camera.start()
        
        time.sleep(0.1)

    # --- IMAGE ACQUISITION AND PROCESSING ---
    def receive_image(self):
        #self.frame = self.camera.read()[1]
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

    # --- DRAWING UTILITIES ---
    def draw_roi(self, roi,color = (0,255,0)):
        cv2.rectangle(self.frame, (roi.x1, roi.y1), (roi.x2, roi.y2), color, 2)

    def draw_contours(self, cnt, roi, color):
        cv2.drawContours(self.frame[roi.y1:roi.y2, roi.x1:roi.x2], cnt, -1, color, 2)

    def draw_centroid_line(self, max_contour_data, roi: ROI, color=(255, 0, 0), thickness=2):
        """
        Recibe el resultado de max_contour [max_area, max_x, max_y, max_cnt].
        Calcula el centroide del contorno más grande y dibuja la línea vertical.
        """
        # Extraer el contorno del arreglo de datos
        max_cnt = max_contour_data[3]
        
        # Si no se encontró ningún contorno válido, salimos de la función
        if max_cnt is None:
            return

        # Calcular los momentos del contorno más grande
        M = cv2.moments(max_cnt)
        if M["m00"] != 0:
            # Calcular X local de la ROI y transformarlo a la imagen global
            global_cx = int(M["m10"] / M["m00"]) + roi.x1
            
            # Dibujar línea vertical contenida en el alto de la ROI
            cv2.line(self.frame, (global_cx, roi.y1), (global_cx, roi.y2), color, thickness)
            
            # Extra: Calcular Y para pintar el punto del centroide
            global_cy = int(M["m01"] / M["m00"]) + roi.y1
            cv2.circle(self.frame, (global_cx, global_cy), 5, color, -1)
            return (global_cx, global_cy)
        else:
            return None

    def draw_parallel_lane_line(self, centroid_coords, roi: ROI, offset=80, avoid_right=True, color=(0, 255, 255), thickness=2):
        """
        Dibuja una l�nea paralela al centroide a una distancia fija (offset).
        
        :param centroid_coords: Tupla (global_cx, global_cy) devuelta por draw_centroid_line.
        :param roi: El objeto ROI actual.
        :param offset: Distancia en p�xeles hacia la izquierda o derecha desde el centroide.
        :param avoid_right: Si es True, dibuja la l�nea a la derecha. Si es False, a la izquierda.
        :param color: Color BGR para la l�nea (por defecto Amarillo).
        """
        # Validar que tengamos un centroide v�lido
        if centroid_coords is None:
            return None

        global_cx, global_cy = centroid_coords

        # Determinar la direcci�n del desplazamiento
        if avoid_right:
            lane_x = global_cx + offset
        else:
            lane_x = global_cx - offset

        # Asegurar que la l�nea no se dibuje fuera de los l�mites de la imagen (640 de ancho)
        lane_x = max(0, min(lane_x, self.image_width))

        # Dibuja la l�nea paralela (desde el l�mite superior al inferior de la ROI)
        cv2.line(self.frame, (lane_x, roi.y1), (lane_x, roi.y2), color, thickness)
        
        # Opcional: Dibujar una flecha indicando la direcci�n de evasi�n
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
    # vision = VisionController()

    # # Definición de ROIs

    # roi2 = ROI(0, 100, 320, 150)
    # roi = ROI(320, 100, 640, 150)
    # while True:
    #     try:
    #         vision.receive_image()
    #         ctn = vision.find_contours([[0,0,0],[60,255,209]], ROI(200, 300, 440, 350))
    #         vision.draw_contours(ctn, ROI(0, 200, 40, 350), (0, 255, 255))
    #         vision.draw_roi(roi)
    #         cv2.imshow('Vision HD - Posicion Corregida', vision.frame)
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break
    #     except Exception as e:
    #         print(f"Error en el bucle principal: {e}")
    
    # cv2.destroyAllWindows()
