import cv2 
from vision_controller import VisionController
from vision_controller import ROI

vision = VisionController()

roi1 = ROI(0, 0, 320, vision.image_height)
roi2 = ROI(320, 0, vision.image_width, vision.image_height)

while True:
    vision.receive_image()
    cnt_green = vision.find_contours([[30, 0, 43 ], [255, 100, 216]], roi1)
    cnt_green_max = vision.max_contour(cnt_green, roi1)
    vision.draw_roi(roi1)
    vision.draw_roi(roi2, color=(0, 0, 255) ) 

    cnt_red = vision.find_contours([[30, 170, 120], [255, 255, 170]], roi2)
    cnt_red_max = vision.max_contour(cnt_red, roi2)

    print(f"Area: {cnt_green_max[0]}")
    print(f"Area: {cnt_red_max[0]}")

    if cnt_green_max[0] > 15000:
        print("Verde esta cerca")
    elif cnt_green_max[0] < 15000 and cnt_green_max[0] > 0:
        print("Verde esta lejos")
    else:
        print("No hay verde")

    if cnt_red_max[0] > 15000:
        print("Rojo esta cerca")
    elif cnt_red_max[0] < 15000 and cnt_red_max[0] > 0:
        print("Rojo esta lejos")
    else:
        print("No hay rojo")

    cv2.imshow('Vision HD - Posicion Corregida', vision.frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break