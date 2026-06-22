from mega_pi_controller import *
from constants import *
import cv2 
import time

# --- INITIALIZATION AND CONFIGURATION ---
LNM = MegaPiController("/dev/ttyUSB0", 115200)

OPEN_ROI_CENTER = ROI(200, 20, 430, 200) 
ROI_LINES = ROI(200, 300, 440, 350)       
ROI_OBSTACULOS = ROI(30, 30, 610, 320)

while not LNM.start():
    pass
running = True

# --- TIMERS Y CONTADORES ---
orange_timer = time.time()
blue_timer = time.time()
loops = 0
n = 0
girando = False  

# --- VARIABLES PARA TIEMPO DE GRACIA ---
tiempo_perdida = 0.0
TIEMPO_GRACIA = 0.2  

# --- PARÁMETROS PID PARA CENTRADO DE LÍNEAS ---
Kp_vision = 0.015    
Ki_vision = 0.0
Kd_vision = 0.035   
prev_error = 0.0
integral = 0.0
MAX_INTEGRAL = 15.0 

# --- PARÁMETROS PID EXCLUSIVOS PARA EVITAR OBSTÁCULOS ---
Kp_obstaculo = 0.28   
Kd_obstaculo = 0.01   

# --- MÁQUINA DE ESTADOS PARA OBSTÁCULOS ---
estado_carrera = "LINEAL"
memoria_lado = None  

# --- CONFIGURACIÓN DE VELOCIDAD Y AJUSTES ---
VELOCIDAD_BASE = 75
DIST_MIN_CHOQUE = 12.0  
steering_angle = 80     

UMBRAL_PIXELES_MUERTO = 150  
TOLERANCIA_ANGULO = 3       

# --- CONFIGURACIÓN PARA EVITAR PAREDES SEGUIDAS ---
DIST_MIN_PARED = 18.0  
DIST_CRITICA_TOFS = 8.0 # Umbral ultra-bajo exclusivo para impacto inminente con PARED

# --- FIN DE CARRERA ---
end_game_triggered = False
end_game_timer = 0.0

# --- ROIs LATERALES ---
roi_izq = ROI(0, 100, 320, 150)  
roi_der = ROI(320, 100, 640, 150)  

def obtener_areas_lineas():
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi_izq)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi_der)
    area_right = LNM.vision.max_contour(blackcnt_right, roi_der)[0]
    area_left = LNM.vision.max_contour(blackcnt_left, roi_izq)[0]
    return [area_right, area_left]

def procesar_obstaculos():
    cnt_rojo = LNM.vision.find_contours(LNM.mask_red, ROI_OBSTACULOS)
    cnt_verde = LNM.vision.find_contours(LNM.mask_green, ROI_OBSTACULOS)
    datos_rojo = LNM.vision.max_contour(cnt_rojo, ROI_OBSTACULOS)
    datos_verde = LNM.vision.max_contour(cnt_verde, ROI_OBSTACULOS)
    return datos_rojo, datos_verde

def draw_all_rois(datos_rojo, datos_verde):
    LNM.vision.draw_roi(roi_izq)
    LNM.vision.draw_roi(roi_der)
    LNM.vision.draw_roi(ROI_OBSTACULOS)
    if datos_rojo[3] is not None:
        LNM.vision.draw_contours([datos_rojo[3]], ROI_OBSTACULOS, (0, 0, 255)) 
    if datos_verde[3] is not None:
        LNM.vision.draw_contours([datos_verde[3]], ROI_OBSTACULOS, (0, 255, 0)) 

# --- MAIN CONTROL LOOP ---
while running:
    try:
        LNM.vision.receive_image()
        LNM.obtener_linea_azul()
        LNM.obtener_linea_naranja()
        LNM.obtenerarea_frontal()
        
        front_dist, left_dist, right_dist, dist_laser1, dist_laser2 = LNM.get_distances()
        
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()
        
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # =========================================================================
        # FRENO DE MANO DE EMERGENCIA TRADICIONAL (Frente)
        # =========================================================================
        if front_dist < DIST_MIN_CHOQUE and front_dist > 1.0:
            print(f"🚨 ¡FRENO DE MANO! Frente obstruido a {front_dist:.2f} cm.")
            LNM.stop(log=False)
            time.sleep(0.05)
            
            angulo_escape_opuesto = 160 - steering_angle
            angulo_escape_opuesto = max(40, min(120, angulo_escape_opuesto))
            if angulo_escape_opuesto == 80:
                angulo_escape_opuesto = 60
                
            LNM.move_backward(angle=angulo_escape_opuesto, speed=85)
            time.sleep(0.75)
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            girando = False
            tiempo_perdida = 0.0 
            time.sleep(0.1)
            continue

        # =========================================================================
        # FILTRO CRÍTICO: DETECCIÓN DE IMPACTO CON PARED (GIRO EXTREMO)
        # El giro extremo solo se activa si no se ve un pilar en esa dirección (Área == 0)
        # =========================================================================
        if estado_carrera in ["ESQUIVANDO", "REBASANDO"]:
            if memoria_lado == "IZQUIERDA" and dist_laser1 < DIST_CRITICA_TOFS and dist_laser1 > 1.0 and datos_verde[0] == 0:
                print(f"🧱 [COLISIÓN PARED IZQ] ToF1: {dist_laser1}cm sin pilar a la vista. ¡Giro Extremo!")
                estado_carrera = "ESCAPE_OBSTACULO"
            elif memoria_lado == "DERECHA" and dist_laser2 < DIST_CRITICA_TOFS and dist_laser2 > 1.0 and datos_rojo[0] == 0:
                print(f"🧱 [COLISIÓN PARED DER] ToF2: {dist_laser2}cm sin pilar a la vista. ¡Giro Extremo!")
                estado_carrera = "ESCAPE_OBSTACULO"

        if estado_carrera != "ESCAPE_OBSTACULO":
            LNM.move_forward(speed=VELOCIDAD_BASE) 

        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # =========================================================================
        # MÁQUINA DE ESTADOS: NAVEGACIÓN Y EVASIÓN DE OBSTÁCULOS
        # =========================================================================
        
        # --- ESTADO DE EMERGENCIA: ESCAPE POR PARED ---
        if estado_carrera == "ESCAPE_OBSTACULO":
            LNM.stop(log=False)
            time.sleep(0.04)
            
            if memoria_lado == "IZQUIERDA":
                LNM.move_backward(angle=120, speed=95) # Latigazo hacia la derecha para alejar la trompa de la pared izq
            else:
                LNM.move_backward(angle=40, speed=95)  # Latigazo hacia la izquierda para alejar la trompa de la pared der
                
            time.sleep(0.55) 
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            tiempo_perdida = 0.0
            estado_carrera = "REBASANDO" 
            time.sleep(0.05)
            continue

        # --- ESTADO 1: LINEAL ---
        elif estado_carrera == "LINEAL":
            if datos_verde[0] > 350 and datos_verde[0] >= datos_rojo[0]:
                print("🟢 ¡Pilar Verde Detectado! Cambiando a ESQUIVANDO.")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "IZQUIERDA" 
                prev_error = 0.0
                tiempo_perdida = 0.0
                girando = False 
            elif datos_rojo[0] > 300 and datos_rojo[0] > datos_verde[0]:
                print("🔴 ¡Pilar Rojo Detectado! Cambiando a ESQUIVANDO.")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "DERECHA"   
                prev_error = 0.0
                tiempo_perdida = 0.0
                girando = False 

            # --- CONTROL DE GIROS EN ESQUINAS CERRADAS ---
            if estado_carrera == "LINEAL":
                if front_dist < 90 and not girando and LNM.black_area > 8000 and LNM.turning_direction != 0:
                    LNM.turn_direction()
                    girando = True
                    
                elif LNM.black_area < 8000 and girando and front_dist > 80:
                    LNM.turn_center()
                    girando = False
                    steering_angle = 80

                if not girando:
                    error = black_areas[1] - black_areas[0]
                    integral += error
                    integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral))
                    derivative = error - prev_error
                    correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
                    prev_error = error
                    
                    steering_angle = int(80 + correction)
                    steering_angle = max(40, min(120, steering_angle))
                    
                    if abs(error) < UMBRAL_PIXELES_MUERTO or abs(steering_angle - 80) <= TOLERANCIA_ANGULO:
                        LNM.turn_center()
                        steering_angle = 80
                    elif steering_angle > 80:
                        LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
                    elif steering_angle < 80:
                        LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 2: ESQUIVANDO ---
        elif estado_carrera == "ESQUIVANDO":
            print(f"🔄 [MODO ESQUIVA]: Evadiendo pilar por la {memoria_lado} | ToF1:{dist_laser1}cm ToF2:{dist_laser2}cm")
            
            SETPOINT_VERDE = 548
            SETPOINT_ROJO = 51
            
            # Alertas de proximidad normales para pilares
            if memoria_lado == "IZQUIERDA" and dist_laser1 < DIST_MIN_PARED and dist_laser1 > 1.0:
                estado_carrera = "REBASANDO"
                continue
            elif memoria_lado == "DERECHA" and dist_laser2 < DIST_MIN_PARED and dist_laser2 > 1.0:
                estado_carrera = "REBASANDO"
                continue
            
            if memoria_lado == "IZQUIERDA": 
                if datos_verde[0] == 0:
                    if tiempo_perdida == 0.0:
                        tiempo_perdida = time.time()  
                    elif (time.time() - tiempo_perdida) > TIEMPO_GRACIA:
                        estado_carrera = "REBASANDO"
                        tiempo_perdida = 0.0
                        continue
                    error_obs = prev_error  
                else:
                    tiempo_perdida = 0.0  
                    error_obs = datos_verde[1] - SETPOINT_VERDE
                
            else: 
                if datos_rojo[0] == 0:
                    if tiempo_perdida == 0.0:
                        tiempo_perdida = time.time()  
                    elif (time.time() - tiempo_perdida) > TIEMPO_GRACIA:
                        estado_carrera = "REBASANDO"
                        tiempo_perdida = 0.0
                        continue
                    error_obs = prev_error  
                else:
                    tiempo_perdida = 0.0  
                    error_obs = datos_rojo[1] - SETPOINT_ROJO
            
            derivative_obs = error_obs - prev_error
            correction_obs = (Kp_obstaculo * error_obs) + (Kd_obstaculo * derivative_obs)
            prev_error = error_obs
            
            steering_angle = int(80 + correction_obs)
            steering_angle = max(40, min(120, steering_angle))
            
            if steering_angle > 80:
                LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
            elif steering_angle < 80:
                LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 3: REBASANDO ---
        elif estado_carrera == "REBASANDO":
            print(f"⏱️ [MODO REBASE]: Esperando liberación lateral. ToF1:{dist_laser1}cm | ToF2:{dist_laser2}cm")
            
            if memoria_lado == "IZQUIERDA":
                if dist_laser1 < DIST_MIN_PARED and dist_laser1 > 1.0:
                    LNM.turn_right(angle=85, speed=VELOCIDAD_BASE) 
                else:
                    LNM.turn_left(angle=72, speed=VELOCIDAD_BASE)  
                
                if dist_laser2 > 40: 
                    print("✅ Pilar verde superado por completo.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0
            
            elif memoria_lado == "DERECHA":
                if dist_laser2 < DIST_MIN_PARED and dist_laser2 > 1.0:
                    LNM.turn_left(angle=75, speed=VELOCIDAD_BASE)  
                else:
                    LNM.turn_right(angle=88, speed=VELOCIDAD_BASE) 
                
                if dist_laser1 > 40: 
                    print("✅ Pilar rojo superado por completo.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0

    except Exception as e:
        print("Exception en el bucle principal:", e)
        break

LNM.stop()
