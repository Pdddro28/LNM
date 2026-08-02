import cv2
import json 
import numpy as np
from vision_controller import VisionController
from vision_controller import ROI

vision = VisionController()

roi1 = ROI(10, 10, vision.image_width - 10, vision.image_height - 120)
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

def deteccion_obstaculos():
    print(f"Hola")

verde = get_masks('verde')
rojo = get_masks('rojo')

set_point_verde = 584
set_point_rojo = 60

error_verde = 0
error_rojo = 0

angulo_centro = 88
angulo_min = 40
angulo_max = 120
angulo_servo = angulo_centro

Kp = 0.1

while True:
    vision.receive_image()

    cnt_green = vision.find_contours(verde, roi1)
    cnt_green_max = vision.max_contour(cnt_green, roi1)

    cnt_red = vision.find_contours(rojo, roi1)
    cnt_red_max = vision.max_contour(cnt_red, roi1)
    
    draw_centroid(vision.frame, cnt_green_max, (0, 255, 0))
    draw_centroid(vision.frame, cnt_red_max, (0, 0, 255))

    vision.draw_roi(roi1)
    vision.draw_contours(cnt_green, roi1, (0, 255, 0))
    vision.draw_contours(cnt_red, roi1, (0, 0, 255))
    vision.draw_roi(roi1, color=(0, 0, 255) ) 

    if cnt_green_max[0] > 5000 and cnt_green_max[0] > cnt_red_max[0]:
        print("Green's Bigger & Close.")
        error_verde = set_point_verde - cnt_green_max[1]
        correccion_izq = Kp * error_verde
        angulo_servo = int(angulo_centro + correccion_izq)
        angulo_servo = int(np.clip(angulo_servo, angulo_min, angulo_max))
        print(f"Error Verde: {error_verde} | Correccion Izq: {correccion_izq}")

    elif cnt_red_max[0] > 5000 and cnt_red_max[0] > cnt_green_max[0]:
        print("Red's Bigger & Close.")
        error_rojo = set_point_rojo - cnt_red_max[1]
        correccion_der = Kp * error_rojo
        angulo_servo = int(angulo_centro + correccion_der)
        angulo_servo = int(np.clip(angulo_servo, angulo_min, angulo_max))
        print(f"Angulo Servo: {angulo_servo}")

    cv2.putText(vision.frame, f"Angulo Servo: {angulo_servo}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow('Vision HD - Posicion Corregida', vision.frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break