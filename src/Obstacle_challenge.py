from mega_pi_controller import *
from constants import *
import cv2 
import time

# --- INITIALIZATION AND CONFIGURATION ---
LNM = MegaPiController("/dev/ttyUSB0", 115200)

OPEN_ROI_CENTER = ROI(200, 20, 430, 200) 
ROI_LINES = ROI(200, 300, 440, 350)       
ROI_OBSTACULOS = ROI(30, 30, 610, 320)

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

# --- CONFIGURACIÓN DE SEGURIDAD PARA PAREDES (ToF LASER) ---
DIST_MIN_PARED = 18.0       # Distancia normal para empezar a rebasar/separarse de muros
DIST_CRITICA_PARED = 7.5    # Umbral de impacto inminente con pared fija (Activa Giro Extremo)

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
    print(f"🔴 Rojo: Área={datos_rojo[0]}, X={datos_rojo[1]}")
    print(f"🟢 Verde: Área={datos_verde[0]}, X={datos_verde[1]}")
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
        
        # Mapeo correcto de distancias físicas
        front_dist, left_dist, right_dist, laser_1, laser_2 = LNM.get_distances()
        
        # Renombramos las variables internas de uso de los ToF para evitar confusiones en la lógica
        tof_izq = laser_1
        tof_der = laser_2
        
        print(f"📡 Telemetría -> Frente: {front_dist:.1f}cm | ToF Izq: {tof_izq:.1f}cm | ToF Der: {tof_der:.1f}cm")
        
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()
        
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # =========================================================================
        # FILTRO CRÍTICO GLOBAL: DETECCIÓN DE IMPACTO CON PARED (GIRO EXTREMO)
        # =========================================================================
        # Solo se ejecuta si estamos esquivando u omitiendo un objeto, la distancia lateral es ínfima,
        # Y la cámara certifica que NO hay un pilar de color interfiriendo la visual en esa dirección.
        if estado_carrera in ["ESQUIVANDO", "REBASANDO"]:
            if memoria_lado == "IZQUIERDA" and 1.0 < tof_izq < DIST_CRITICA_PARED and datos_verde[0] == 0:
                print(f"🧱 [CRÍTICO] Colisión inminente pared IZQUIERDA ({tof_izq}cm). Forzando Giro Extremo.")
                estado_carrera = "ESCAPE_PARED"
            elif memoria_lado == "DERECHA" and 1.0 < tof_der < DIST_CRITICA_PARED and datos_rojo[0] == 0:
                print(f"🧱 [CRÍTICO] Colisión inminente pared DERECHA ({tof_der}cm). Forzando Giro Extremo.")
                estado_carrera = "ESCAPE_PARED"

        # =========================================================================
        # FRENO DE MANO DE EMERGENCIA FRONTAL
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

        if estado_carrera != "ESCAPE_PARED":
            LNM.move_forward(speed=VELOCIDAD_BASE) 

        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # =========================================================================
        # MÁQUINA DE ESTADOS: NAVEGACIÓN Y EVASIÓN DE OBSTÁCULOS
        # =========================================================================
        
        # --- ESTADO DE EMERGENCIA: MANIOBRA DE LATIGAZO ---
        if estado_carrera == "ESCAPE_PARED":
            LNM.stop(log=False)
            time.sleep(0.04)
            # Marcha atrás con contraviraje violento para enderezar el chasis respecto a la pared lateral
            if memoria_lado == "IZQUIERDA":
                LNM.move_backward(angle=120, speed=95) 
            else:
                LNM.move_backward(angle=40, speed=95)  
                
            time.sleep(0.6) 
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            tiempo_perdida = 0.0
            estado_carrera = "REBASANDO" # Retorna a rebase controlado para seguir adelante alejado del muro
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

        # --- ESTADO 2: ESQUIVANDO (Controlado por Visión PID) ---
        elif estado_carrera == "ESQUIVANDO":
            SETPOINT_VERDE = 548
            SETPOINT_ROJO = 51
            
            # Corrección de lectura: Usamos ToF reales para saltar a Rebozado si nos acercamos de manera estándar a un muro
            if memoria_lado == "IZQUIERDA" and 1.0 < tof_izq < DIST_MIN_PARED:
                print("⚠️ Proximidad lateral izquierda regular detectada por ToF. Transición a REBASANDO.")
                estado_carrera = "REBASANDO"
                continue
            elif memoria_lado == "DERECHA" and 1.0 < tof_der < DIST_MIN_PARED:
                print("⚠️ Proximidad lateral derecha regular detectada por ToF. Transición a REBASANDO.")
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

        # --- ESTADO 3: REBASANDO (Guiado por los sensores ToF Láser) ---
        elif estado_carrera == "REBASANDO":
            if memoria_lado == "IZQUIERDA":
                if 1.0 < tof_izq < DIST_MIN_PARED:
                    LNM.turn_right(angle=86, speed=VELOCIDAD_BASE) # Abre levemente a la derecha si sigue muy cerca del muro izq
                else:
                    LNM.turn_left(angle=74, speed=VELOCIDAD_BASE)  # Retorna de forma sutil al centro
                
                # Criterio de liberación: El ToF derecho lee espacio libre y ya pasó el pilar
                if tof_der > 42: 
                    print("✅ Obstáculo verde dejado atrás de manera segura.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0
            
            elif memoria_lado == "DERECHA":
                if 1.0 < tof_der < DIST_MIN_PARED:
                    LNM.turn_left(angle=74, speed=VELOCIDAD_BASE)  # Abre levemente a la izquierda si sigue muy cerca del muro der
                else:
                    LNM.turn_right(angle=86, speed=VELOCIDAD_BASE) # Retorna sutilmente
                
                if tof_izq > 42: 
                    print("✅ Obstáculo rojo dejado atrás de manera segura.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0

    except Exception as e:
        print("Exception en el bucle principal:", e)
        break

LNM.stop()
