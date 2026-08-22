from mega_pi_controller import *
from constants import *
import cv2 
import time

# --- INITIALIZATION AND CONFIGURATION ---
LNM = MegaPiController("/dev/ttyUSB0", 115200)

ROIS = [OPEN_ROI_CENTER, ROI_LINES]

states = {"straight": False, "girando": False}

while LNM.start():
    pass
running = True
loops = 0

orange_timer = time.time()
blue_timer = time.time()
time_lap = time.time()
n = 0

# --- NUEVOS PARÁMETROS PID PARA CONTROL VISUAL ---
Kp_vision = 0.015    
Ki_vision = 0.0
Kd_vision = 0.005   

prev_error = 0.0
integral = 0.0
MAX_INTEGRAL = 15.0 
girando = False
conteo = False

# --- CONFIGURACIÓN DEL FRENO DE MANO DE EMBERGENCIA ---
DIST_MIN_CHOQUE = 12.0  
steering_angle = 80     

# --- VARIABLES DE TOLERANCIA (EVITAR ZIGZAGUEO) ---
UMBRAL_PIXELES_MUERTO = 150  # Ignora errores de área menores a este valor
TOLERANCIA_ANGULO = 3       # Si el ángulo está entre 77 y 83 (80 +/- 3), va recto

# --- VARIABLES PARA FIN DE CARRERA NO BLOQUEANTE ---
end_game_triggered = False
end_game_timer = 0.0

# --- CONFIGURACIÓN DE ROIS LATERALES ---
roi2 = ROI(0, 100, 320, 150)  # ROI Izquierda
roi = ROI(320, 100, 640, 150)  # ROI Derecha

black_area_right = 0
black_area_left = 0
blackcnt_right = None
blackcnt_left = None

def obtener_areas():
    global black_area_right, black_area_left, blackcnt_right, blackcnt_left
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi2)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi)
    black_area_right = LNM.vision.max_contour(blackcnt_right, roi)[0]
    black_area_left = LNM.vision.max_contour(blackcnt_left, roi2)[0]
    return [black_area_right, black_area_left]

def draw_rois():
    LNM.vision.draw_roi(roi)
    LNM.vision.draw_roi(roi2)
    LNM.vision.draw_contours(blackcnt_left, roi2, (0, 255, 255))
    LNM.vision.draw_contours(blackcnt_right, roi, (0, 255, 255))

# --- MAIN CONTROL LOOP ---
while running:
    try:
        # Sensors and data acquisition
        LNM.vision.receive_image()
        LNM.obtener_linea_azul()
        LNM.obtener_linea_naranja()
        LNM.obtenerarea_frontal()
        
        black_areas = obtener_areas()
        draw_rois()

        #cv2.imshow('Vision HD - Posicion Corregida', LNM.vision.frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
           # break

        # Recibe los 4 datos de la tupla (manteniendo tus 3 originales + 1 temporal ignorado)
        front_dist, left_dist, right_dist, dist_laser1, dist_laser2 = LNM.get_distances()
        print(f"front: {front_dist} | Right: {right_dist}cm | Left: {left_dist}cm")
        
        # =========================================================================
        # FRENO DE MANO DE EMERGENCIA (Basado en proximidad física frontal)
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
            time.sleep(0.1)
            continue

        # Avanzamos con la velocidad normal del Open Challenge
        LNM.move_forward(speed=130) 

        # 1. TRACK TYPE DETECTION
        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # 2. CORNER DETECTION (Detección de Esquinas para Cruzar)
        if front_dist < 85 and not girando and LNM.black_area > 8000 and LNM.turning_direction != 0:
            LNM.turn_direction()
            girando = True

            prev_error = 0.0
            integral = 0.0
              
        if LNM.black_area < 8000 and girando and front_dist > 80:
           LNM.turn_center()
           girando = False
           conteo = False
           steering_angle = 80

        # =========================================================================
        # ESTRATEGIA DE CENTRADO MEDIANTE DIFERENCIA DE ÁREAS (PID VISUAL)
        # =========================================================================
        if not girando and LNM.turning_direction != 0:
            # Error = Izquierda - Derecha
            error = black_areas[1] - black_areas[0]
            
            # Control integral con filtro anti-windup
            integral += error
            integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral))
            
            derivative = error - prev_error
            correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
            prev_error = error
            
            # Cálculo del ángulo base
            steering_angle = int(80 + correction)
            steering_angle = max(40, min(120, steering_angle))
            print(f"Error: {error}, Integral: {integral:.2f}, Derivative: {derivative}, Steering Angle: {steering_angle}")
            
            # --- FILTROS DE TOLERANCIA SUAVE (Evita movimientos constantes en rectas) ---
            if abs(error) < UMBRAL_PIXELES_MUERTO: 
                LNM.turn_center()
                steering_angle = 80
            elif abs(steering_angle - 80) <= TOLERANCIA_ANGULO:
                LNM.turn_center()
                steering_angle = 80
            elif steering_angle > 80:
                LNM.turn_right(angle=steering_angle, speed=130)
            elif steering_angle < 80:
                LNM.turn_left(angle=steering_angle, speed=130)

        # =========================================================================
        # 3. LOGIC AND LAP COUNTER & CRONÓMETRO DINÁMICO DE CIERRE
        # =========================================================================
        current_time = time.time()

        if LNM.orange_area > 500 and n == 0 and LNM.turning_direction == 2: 
            orange_timer = current_time
            n = 1
            loops += 1

        if LNM.blue_area > 500 and n == 0 and LNM.turning_direction == 1: 
            blue_timer = current_time
            n = 1
            loops += 1

        if current_time - orange_timer > 1.1 and LNM.turning_direction == 2: 
            n = 0

        if current_time - blue_timer > 1.1 and LNM.turning_direction == 1:
            n = 0

        # Control asíncrono para el fin de carrera (3 segundos extra manteniendo lógica)
        if loops >= 12 and not end_game_triggered:
            print("🏁 ¡Vuelta 12 alcanzada! Iniciando cronómetro de 3 segundos de gracia...")
            end_game_timer = current_time
            end_game_triggered = True

        if end_game_triggered:
            if current_time - end_game_timer >= 1:
                print("⏱️ Tiempo de gracia completado. Deteniendo robot.")
                break
        
    except Exception as e:
        print("Exception:", e)
        LNM.stop()
        break

# --- SAFETY SHUTDOWN ---
LNM.stop()
