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
VELOCIDAD_BASE = 75  # Bajamos levemente a 70 para ganar control en zonas densas
DIST_MIN_CHOQUE = 10.0  
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
roi_izq_inner = ROI(290, 100, 330, 150)  

def obtener_areas_lineas():
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi_izq)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi_der)

    area_right = LNM.vision.max_contour(blackcnt_right, roi_der)[0]
    LNM.vision.draw_contours(blackcnt_right,roi_der,(0,0,255))

    area_left = LNM.vision.max_contour(blackcnt_left, roi_izq)[0]
    LNM.vision.draw_contours(blackcnt_left,roi_izq,(0,0,255))

    blackcnt_left_avoid = LNM.vision.find_contours(LNM.mask_black, roi_izq_inner)
    area_avoid_left = LNM.vision.max_contour(blackcnt_left_avoid,roi_izq_inner)[0]

    return [area_right, area_left, area_avoid_left]

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
    LNM.vision.draw_roi(roi_izq_inner,(0,0,255))
    if datos_rojo[3] is not None:
        LNM.vision.draw_contours([datos_rojo[3]], ROI_OBSTACULOS, (0, 0, 255)) 
    if datos_verde[3] is not None:
        LNM.vision.draw_contours([datos_verde[3]], ROI_OBSTACULOS, (0, 255, 0)) 

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
        
        print(estado_carrera)
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # TRACK TYPE DETECTION
        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # ---------------------------------------------------------------------
        # 🚨 NUEVO: GATILLO FRENO DE MANO POR ATASQUE VISUAL (STALL DETECTION)
        # ---------------------------------------------------------------------
        if LNM.vision.check_if_stuck():
            print("\n🚨 ¡FRENO DE MANO ACTIVADO! El carro está físicamente atrapado (Entorno estático).")
            LNM.stop(log=False)
            
            # Maniobra de liberación: Retroceder recto para desencajarse de la pared/obstáculo invisible
            print("🌀 [SISTEMA ANTI-ATASQUE] Retrocediendo RECTO de emergencia para liberar chasis.")
            LNM.move_backward(angle=80, speed=85)
            time.sleep(1.0)
            
            # Limpieza de estados y continuación segura
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            tiempo_perdida = 0.0 
            LNM.vision.reset_stuck_timer() # Limpiamos historial para no re-activar al salir
            time.sleep(0.1)
            continue

        # ---------------------------------------------------------------------
        # FRENO DE MANO CONVENCIONAL POR DISTANCIA FRONTAL
        # ---------------------------------------------------------------------
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
            LNM.vision.reset_stuck_timer() # Evita falsos positivos tras haber estado detenido en la maniobra
            time.sleep(0.1)
            continue

        # NAVEGACIÓN ACTIVA
        LNM.move_forward(VELOCIDAD_BASE)
        
        # --- ESTADO 1: LINEAL ---
        if estado_carrera == "LINEAL":
            if front_dist < 55 and LNM.black_area > 6000 and LNM.turning_direction != 0:
                pass

            if datos_verde[0] > 350 and datos_verde[0] >= datos_rojo[0]:
                print("🟢 Transición -> ESQUIVANDO (Pilar Verde).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "IZQUIERDA"
                LNM.vision.reset_stuck_timer() # Reset al cambiar bruscamente de estado
                
            elif datos_rojo[0] > 250 and datos_rojo[0] >= datos_verde[0]:
                print("🔴 Transición -> ESQUIVANDO (Pilar Rojo).")
                estado_carrera = "ESQUIVANDO"
                memoria_lado = "DERECHA"
                LNM.vision.reset_stuck_timer()

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
                    LNM.turn_right(angle = steering_angle, speed = VELOCIDAD_BASE)
                elif steering_angle < 80:
                    LNM.turn_left(angle = steering_angle, speed = VELOCIDAD_BASE)
        
        # --- ESTADO 2: ESQUIVANDO ---
        elif estado_carrera == "ESQUIVANDO":
            SETPOINT_VERDE = 548
            SETPOINT_ROJO = 51

            if memoria_lado == "IZQUIERDA":
                error_obs = datos_verde[1] - SETPOINT_VERDE
                if tiempo_perdida == 0.0:
                    tiempo_perdida = time.time()
                elif (time.time() - tiempo_perdida) > TIEMPO_GRACIA:
                    estado_carrera = "LINEAL"
                    tiempo_perdida = 0.0
                    memoria_lado = ""
                    LNM.vision.reset_stuck_timer()
            else:
                error_obs = datos_rojo[1] - SETPOINT_ROJO
                if tiempo_perdida == 0.0:
                    tiempo_perdida = time.time()
                elif (time.time() - tiempo_perdida) > 0.51:
                    estado_carrera = "LINEAL"
                    tiempo_perdida = 0.0
                    memoria_lado = ""
                    LNM.vision.reset_stuck_timer()

            derivative_obs = error_obs - prev_error
            correction_obs = (Kp_obstaculo * error_obs) + (Kd_obstaculo * derivative_obs)
            
            prev_error = error_obs

            steering_angle = int(80 + correction_obs)
            steering_angle = max(40, min(120, steering_angle))

            if (black_areas[2] > 100) and memoria_lado == "IZQUIERDA":
                    print("CORRIGIENDO")
                    LNM.turn_right(120, speed = VELOCIDAD_BASE + 30)
                    continue
            if steering_angle > 80:
                LNM.turn_right(angle = steering_angle, speed = VELOCIDAD_BASE)
                    
            elif steering_angle < 80:
                LNM.turn_left(angle = steering_angle, speed = VELOCIDAD_BASE)
                
    except Exception as e:
        print("Error crítico ejecutando el bucle:", e)
        break

LNM.stop()
cv2.destroyAllWindows()
