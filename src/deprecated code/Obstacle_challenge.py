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
tiempo_perdida = 0.0
TIEMPO_GRACIA = 0.35  # Aumentado para dar margen de seguridad en transiciones seguidas

# --- CONTROLLER DE BLOQUEO (ANTI-VOLTEO) ---
ultimo_freno_time = 0.0
frenos_consecutivos = 0

# --- PARÁMETROS PID NAVEGACIÓN ---
Kp_vision = 0.015    
Ki_vision = 0.0
Kd_vision = 0.035   
prev_error = 0.0
integral = 0.0
MAX_INTEGRAL = 15.0 

# --- PARÁMETROS NAVEGACIÓN OBSTÁCULOS ---
Kp_obstaculo = 0.28   
Kd_obstaculo = 0.01   

# --- CONFIGURACIÓN DE SEPARACIÓN PROPORCIONAL DE PAREDES (CRUCIAL) ---
Kp_pared = 1.6  # Fuerza con la que se aleja de las paredes usando los ToF/Ultrasonidos

# --- MÁQUINA DE ESTADOS ---
estado_carrera = "LINEAL"
memoria_lado = None  

# --- CONFIGURACIÓN DE VELOCIDAD Y AJUSTES ---
VELOCIDAD_BASE = 70  # Bajamos levemente a 70 para ganar control en zonas densas
DIST_MIN_CHOQUE = 14.0  
steering_angle = 80     

UMBRAL_PIXELES_MUERTO = 150  
TOLERANCIA_ANGULO = 3       

# --- UMBRALES DE DISTANCIA (Muros Fijos) ---
DIST_DESEADA_PARED = 22.0  # El robot intentará mantenerse idealmente a esta distancia del muro lateral
DIST_MIN_PARED = 16.0      # Límite de aviso de proximidad normal
DIST_CRITICA_PARED = 8.5   # Umbral de impacto inminente con pared fija

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
        
        front_dist, left_dist, right_dist, laser_1, laser_2 = LNM.get_distances()
        
        # Asignación explícita de sensores ToF de alta velocidad
        tof_izq = laser_1
        tof_der = laser_2
        
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()
        
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # =========================================================================
        # FILTRO CRÍTICO SEGURIDAD: IMPACTO LATERAL CON PARED
        # =========================================================================
        if estado_carrera in ["ESQUIVANDO", "REBASANDO"]:
            if memoria_lado == "IZQUIERDA" and 1.0 < tof_izq < DIST_CRITICA_PARED and datos_verde[0] == 0:
                print(f"🧱 [MURO] ToF Izquierdo colapsando ({tof_izq}cm). Forzando ESCAPE.")
                estado_carrera = "ESCAPE_PARED"
            elif memoria_lado == "DERECHA" and 1.0 < tof_der < DIST_CRITICA_PARED and datos_rojo[0] == 0:
                print(f"🧱 [MURO] ToF Derecho colapsando ({tof_der}cm). Forzando ESCAPE.")
                estado_carrera = "ESCAPE_PARED"

        # =========================================================================
        # FRENO DE MANO INTELIGENTE (ANTI-VOLTEO)
        # =========================================================================
        if front_dist < DIST_MIN_CHOQUE and front_dist > 1.0:
            current_time = time.time()
            LNM.stop(log=False)
            
            # Verificamos si los impactos frontales son repetitivos en ráfaga (ciclo errático)
            if (current_time - ultimo_freno_time) < 3.0:
                frenos_consecutivos += 1
            else:
                frenos_consecutivos = 1
                
            ultimo_freno_time = current_time
            print(f"🚨 FRENO DE MANO N°{frenos_consecutivos}! Distancia frontal: {front_dist:.1f} cm.")
            
            if frenos_consecutivos >= 2:
                # TRATAMIENTO ANTIBLOQUEO: Salir en línea recta hacia atrás de forma controlada sin rotar el coche
                print("🌀 [SISTEMA ANTI-VOLTEO] Bloqueo cíclico detectado. Retrocediendo RECTO para salvar orientación.")
                LNM.move_backward(angle=80, speed=85)
                time.sleep(0.9)
                frenos_consecutivos = 0
            else:
                # Escape angular normal si es un evento aislado
                angulo_escape_opuesto = 160 - steering_angle
                angulo_escape_opuesto = max(45, min(115, angulo_escape_opuesto))
                if angulo_escape_opuesto == 80: 
                    angulo_escape_opuesto = 65
                LNM.move_backward(angle=angulo_escape_opuesto, speed=85)
                time.sleep(0.7)
                
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            tiempo_perdida = 0.0 
            time.sleep(0.1)
            continue

        if estado_carrera != "ESCAPE_PARED":
            LNM.move_forward(speed=VELOCIDAD_BASE) 

        # =========================================================================
        # NAVEGACIÓN MEDIANTE MÁQUINA DE ESTADOS REVISADA
        # =========================================================================
        
        # --- ESTADO DE EMERGENCIA: MANIOBRA DE ALINEACIÓN ---
        if estado_carrera == "ESCAPE_PARED":
            LNM.stop(log=False)
            time.sleep(0.03)
            if memoria_lado == "IZQUIERDA":
                LNM.move_backward(angle=115, speed=90) # Saca la trompa con cuidado hacia la derecha
            else:
                LNM.move_backward(angle=45, speed=90)  # Saca la trompa hacia la izquierda
            time.sleep(0.5)
            LNM.turn_center(log=False)
            estado_carrera = "REBASANDO"
            continue

        # --- ESTADO 1: LINEAL ---
        elif estado_carrera == "LINEAL":
            # Filtro visual de entrada: Priorizamos el pilar que tenga mayor área visible en la ROI central
            if datos_verde[0] > 350 and datos_verde[0] >= datos_rojo[0]:
                print("🟢 Transición -> ESQUIVANDO (Pilar Verde).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "IZQUIERDA"
                prev_error = 0.0
                tiempo_perdida = 0.0
            elif datos_rojo[0] > 300 and datos_rojo[0] > datos_verde[0]:
                print("🔴 Transición -> ESQUIVANDO (Pilar Rojo).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "DERECHA"
                prev_error = 0.0
                tiempo_perdida = 0.0

            if estado_carrera == "LINEAL":
                # Centrado de líneas convencional
                error = black_areas[1] - black_areas[0]
                integral += error
                integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral))
                derivative = error - prev_error
                correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
                prev_error = error
                
                steering_angle = int(80 + correction)
                steering_angle = max(45, min(115, steering_angle))
                
                if abs(error) < UMBRAL_PIXELES_MUERTO:
                    LNM.turn_center()
                    steering_angle = 80
                elif steering_angle > 80:
                    LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
                elif steering_angle < 80:
                    LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 2: ESQUIVANDO ---
        elif estado_carrera == "ESQUIVANDO":
            SETPOINT_VERDE = 548
            SETPOINT_ROJO = 51
            
            # Interrupción por proximidad a pared: Si nos acercamos a los muros, pasamos de inmediato al control de rebase por ToF
            if memoria_lado == "IZQUIERDA" and 1.0 < tof_izq < DIST_MIN_PARED:
                estado_carrera = "REBASANDO"
                continue
            elif memoria_lado == "DERECHA" and 1.0 < tof_der < DIST_MIN_PARED:
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

        # --- ESTADO 3: REBASANDO PROPORCIONAL (ENFOQUE MEJORADO BASADO EN SENSORES LÁSER/PARED) ---
        elif estado_carrera == "REBASANDO":
            print(f"🧱 [REBASE SEGURO] Guiado por muros. ToF Izq: {tof_izq:.1f}cm | ToF Der: {tof_der:.1f}cm")
            
            if memoria_lado == "IZQUIERDA":
                # Calculamos un error respecto a la distancia que queremos mantener de la pared izquierda
                error_muro = DIST_DESEADA_PARED - tof_izq
                # Si el error es positivo significa que estamos más cerca de lo ideal -> Girar a la derecha (ángulo > 80)
                ajuste_direccion = int(80 + (error_muro * Kp_pared))
                steering_angle = max(80, min(110, ajuste_direccion)) # Limitamos el ángulo para que no derrape la cola
                LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
                
                # Criterio de liberación definitivo: El sensor derecho (externo) ve pista libre,
                # y no tenemos un pilar verde pegado enfrente en la cámara.
                if tof_der > 45 and datos_verde[0] < 200:
                    print("✅ Pared izquierda y obstáculo verde superados de forma estable.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0
            
            elif memoria_lado == "DERECHA":
                # Calculamos error respecto a la pared derecha
                error_muro = DIST_DESEADA_PARED - tof_der
                # Si estamos muy cerca, error_muro es positivo -> Restamos a 80 para girar a la izquierda
                ajuste_direccion = int(80 - (error_muro * Kp_pared))
                steering_angle = max(50, min(80, ajuste_direccion))
                LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)
                
                if tof_izq > 45 and datos_rojo[0] < 200:
                    print("✅ Pared derecha y obstáculo rojo superados de forma estable.")
                    estado_carrera = "LINEAL"
                    prev_error = 0.0

    except Exception as e:
        print("Error crítico ejecutando el bucle:", e)
        break

LNM.stop()
