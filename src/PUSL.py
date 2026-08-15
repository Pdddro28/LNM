import cv2
import json 
import numpy as np
import time
from mega_pi_controller import *
from vision_controller import VisionController
from vision_controller import ROI
from Timer import TemporizadorNoBloqueante

LNM = MegaPiController("/dev/ttyUSB0", 115200)

roi1 = ROI(10, 10, LNM.vision.image_width - 10, LNM.vision.image_height - 120)
roi2 = ROI(550, 190, LNM.vision.image_width - 10, LNM.vision.image_height - 10)
roi3 = ROI(10, 190, LNM.vision.image_width - 550, LNM.vision.image_height - 10)

timer = TemporizadorNoBloqueante(1)  # 1 segundo
timer_patras = TemporizadorNoBloqueante(2)  # 2 segundos


def get_masks(color):
    with open(f'src/Colors/mask_{color}.json') as f:
        config = json.load(f)
    lower = config['bounds']['lower']
    upper = config['bounds']['upper']
    return [lower, upper]

def draw_centroid(img, max_cnt, color=(255, 0, 0)):
    """Draws a circle at the centroid of the maximum contour on the image.

    Arg: 
        img: The image on which to draw.
        max_cnt: A tuple containing the maximum contour data (area, x, y, contour).
        color: The color of the circle to draw (default is blue).

    Return:
        None
    """
    _, x, y, _ = max_cnt
    cv2.circle(img, (x, y), 5, color, -1)

verde = get_masks('verde')
rojo = get_masks('rojo')
negro = get_masks('negro')
naranja = get_masks('naranja')
azul = get_masks('azul')

set_point_verde = 584
set_point_rojo = 60

error_verde = 0
error_rojo = 0

angulo_centro = 88
angulo_min = 40
angulo_max = 120
angulo_servo = angulo_centro

Kp = 0.1

esquina = False

ESTADO_CARRERA = "INICIANDO"

while True:
    try:
        LNM.vision.receive_image()
        LNM.obtener_linea_azul()
        LNM.obtenerarea_frontal()
        LNM.obtener_linea_naranja()

        cnt_black = LNM.vision.find_contours(negro, roi2)
        cnt_black_max = LNM.vision.max_contour(cnt_black, roi2)

        cnt_black2 = LNM.vision.find_contours(negro, roi3)
        cnt_black_max2 = LNM.vision.max_contour(cnt_black2, roi3)

        cnt_green = LNM.vision.find_contours(verde, roi1)
        cnt_green_max = LNM.vision.max_contour(cnt_green, roi1)

        cnt_red = LNM.vision.find_contours(rojo, roi1)
        cnt_red_max = LNM.vision.max_contour(cnt_red, roi1)
    
        draw_centroid(LNM.vision.frame, cnt_green_max, (0, 255, 0))
        draw_centroid(LNM.vision.frame, cnt_red_max, (0, 0, 255))

        LNM.vision.draw_roi(roi1)
        LNM.vision.draw_roi(LNM.rois[0], color=(0, 255, 0))
        LNM.vision.draw_roi(LNM.rois[1], color=(0, 255, 255))
        LNM.vision.draw_roi(roi1, color=(0, 0, 255)) 
        LNM.vision.draw_roi(roi2, color=(0, 100, 255))
        LNM.vision.draw_roi(roi3, color=(0, 100, 255))

        LNM.vision.draw_contours(cnt_green, roi1, (0, 255, 0))
        LNM.vision.draw_contours(cnt_red, roi1, (0, 0, 255))

        cv2.putText(LNM.vision.frame, f"Area negra: {cnt_black_max[0]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
        cv2.putText(LNM.vision.frame, f"Area negra 2: {cnt_black_max2[0]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)

        cv2.imshow('Vision HD - Posicion Corregida', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        front_dist, left_dist, right_dist, dist_laser1, dist_laser2 = LNM.get_distances() #Variables para obtener las distancias de diferentes ultrasonidos

        if LNM.turning_direction == 0: #Detecta el sentido del carro usando el primer color detectado (solo naranja y azul)
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        if ESTADO_CARRERA == "INICIANDO": #Si el estado es igual a iniciando el carro mueve hacia delante
            LNM.move_forward(90, log=False)
            
            if cnt_green_max[0] > 5000 and cnt_green_max[0] > cnt_red_max[0]: #Usamos el area del color verde y el color rojo para calcular el angulo de giro derecho
                error_verde = set_point_verde - cnt_green_max[1]
                correccion_izq = Kp * error_verde
                angulo_servo_derecha = int(angulo_centro + correccion_izq)
                angulo_servo_derecha_exacta = int(np.clip(angulo_servo_derecha, angulo_min, angulo_max))

                LNM.turn_left(angle=angulo_servo_derecha_exacta, speed=70, log=False)
                ESTADO_CARRERA = "GIRANDO_DERECHA"
                timer.iniciar()
                
            elif cnt_red_max[0] > 5000 and cnt_red_max[0] > cnt_green_max[0]: #Usamos el area del color verde y el color rojo para calcular el angulo de giro izquierdo
                error_rojo = set_point_rojo - cnt_red_max[1]
                correccion_der = Kp * error_rojo
                angulo_servo_izquierda = int(angulo_centro + correccion_der)
                angulo_servo_izquierda_exacta = int(np.clip(angulo_servo_izquierda, angulo_min, angulo_max))

                LNM.turn_right(angle=angulo_servo_izquierda_exacta, speed=80, log=False)

                ESTADO_CARRERA = "GIRANDO_IZQUIERDA"
                timer.iniciar()

            elif LNM.orange_area >= 1200 or LNM.blue_area >= 1200: #Si detecta el color naranja o azul, el carro se detiene y el variable de la esquina se vuelve verdadero
                esquina = True

            elif front_dist < 15 and esquina == True: #Si la distancia frontal tiene menos de 15 cm y la variable de la esquina es verdadera, el carro retrocede y el estado de carrera cambia a retroceso
                ESTADO_CARRERA = "RETROCESO"
                timer_patras.iniciar()

        elif ESTADO_CARRERA == "RETROCESO": #Si el estado de carrera es retroceso, el carro retrocede y si la distancia frontal es mayor a 15 cm
            LNM.move_backward(angle=45, speed=100, log=False)

            if LNM.turning_direction == 1 and right_dist > 65: #Si el sentido de giro es 1 y la distancia es mas de 65, el estado se vuelve iniciando
                ESTADO_CARRERA = "INICIANDO"
                LNM.turn_center()

            elif LNM.turning_direction == 2 and left_dist > 65: #Si el sentido de giro es 2 y la distancia es mas de 65, el estado se vuelve iniciando
                ESTADO_CARRERA = "INICIANDO"
                LNM.turn_center()

        elif cnt_red_max[0] < 4500 and ESTADO_CARRERA == "GIRANDO_IZQUIERDA": #Si el area del color rojo es menor a 5000 y el estado de carrera es girando izquierda, el carro gira a la derecha
            LNM.turn_right(angle=120, speed=80, log=False)
            if timer.ha_expirado(): #Si el temporizador termino, el estado se vuelve iniciando
                ESTADO_CARRERA = "INICIANDO"
                LNM.turn_center()

        elif cnt_green_max[0] < 4500 and ESTADO_CARRERA == "GIRANDO_DERECHA":
            LNM.turn_left(angle=50, speed=80, log=False)
            if timer.ha_expirado():
                ESTADO_CARRERA = "INICIANDO" #
                LNM.turn_center()

        elif cnt_black_max[0] > 1000 and ESTADO_CARRERA == "INICIANDO":
            LNM.turn_left(angle=50, speed=80, log=False)
            kk

        print(f"front: {front_dist}")

        print(f"Estado Carrera: {ESTADO_CARRERA}")

    except Exception as e:
            print("Error crítico ejecutando el bucle:", e)
            break