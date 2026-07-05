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
TIEMPO_GRACIA = 0.2  
tiempo_inicio_retroceso = 0.0  # Temporizador dedicado para la maniobra de esquina

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

# --- CONFIGURACIÓN DE SEPARACIÓN PROPORCIONAL DE PAREDES ---
Kp_pared = 1.6  

# --- MÁQUINA DE ESTADOS REESTRUCTURADA (5 ESTADOS DE ESQUINA) ---
# Estados: "LINEAL", "BUSCAR_LINEA", "LINEA_ENCONTRADA", "INICIO_RETROCESO", "RETROCESO"
estado_carrera = "LINEAL"
memoria_lado = None  

# --- CONFIGURACIÓN DE VELOCIDAD Y AJUSTES ---
VELOCIDAD_BASE = 68  
DIST_MIN_CHOQUE = 10.0  
steering_angle = 80     

UMBRAL_PIXELES_MUERTO = 150  
TOLERANCIA_ANGULO = 3        

# --- UMBRALES DE DISTANCIA (Muros Fijos) ---
DIST_DESEADA_PARED = 22.0  
DIST_MIN_PARED = 16.0      
DIST_CRITICA_PARED = 8.5   

# --- ROIs LATERALES ---
roi_izq = ROI(0, 100, 320, 150)  
roi_der = ROI(320, 100, 640, 150)  
roi_izq_inner = ROI(290, 100, 330, 150)  

def obtener_areas_lineas():
    blackcnt_left = LNM.vision.find_contours(LNM.mask_black, roi_izq)
    blackcnt_right = LNM.vision.find_contours(LNM.mask_black, roi_der)

    area_right = LNM.vision.max_contour(blackcnt_right, roi_der)[0]
    LNM.vision.draw_contours(blackcnt_right, roi_der, (0,0,255))

    area_left = LNM.vision.max_contour(blackcnt_left, roi_izq)[0]
    LNM.vision.draw_contours(blackcnt_left, roi_izq, (0,0,255))

    blackcnt_left_avoid = LNM.vision.find_contours(LNM.mask_black, roi_izq_inner)
    area_avoid_left = LNM.vision.max_contour(blackcnt_left_avoid, roi_izq_inner)[0]

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
    LNM.vision.draw_roi(roi_izq_inner, (0,0,255))
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
        
        # Lectura exclusiva de Ultrasonidos (se ignoran las variables de los láseres)
        front_dist, left_dist, right_dist, _, _ = LNM.get_distances()
        
        black_areas = obtener_areas_lineas()
        datos_rojo, datos_verde = procesar_obstaculos()
        
        print(f"Estado Actual: {estado_carrera} | F:{front_dist:.1f} L:{left_dist:.1f} R:{right_dist:.1f}")
        draw_all_rois(datos_rojo, datos_verde)
        cv2.imshow('Vision HD - Obstacle Challenge', LNM.vision.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # DETECCIÓN AUTOMÁTICA DEL SENTIDO DE GIRO DE LA PISTA
        if LNM.turning_direction == 0: 
            if LNM.orange_area > 1200:
                 LNM.turning_direction = 2
            elif LNM.blue_area > 1200:
                 LNM.turning_direction = 1

        # ---------------------------------------------------------------------
        # DETECCIÓN DE ATASQUE VISUAL (STALL DETECTION)
        # ---------------------------------------------------------------------
        if LNM.vision.check_if_stuck() and estado_carrera != "RETROCESO":
            print("\n🚨 [STUCK] Carro atrapado. Reseteando a LINEAL.")
            LNM.stop(log=False)
            LNM.move_backward(angle=80, speed=85)
            time.sleep(1.0)
            LNM.turn_center(log=False)
            prev_error = 0.0
            integral = 0.0
            estado_carrera = "LINEAL" 
            tiempo_perdida = 0.0 
            LNM.vision.reset_stuck_timer()
            continue

        # ---------------------------------------------------------------------
        # GESTIÓN DETALLADA DE LA MÁQUINA DE 5 ESTADOS
        # ---------------------------------------------------------------------
        
        # --- ESTADO 1: LINEAL ---
        if estado_carrera == "LINEAL":
            # Avanza normalmente y delega la búsqueda de la línea de la esquina
            estado_carrera = "BUSCAR_LINEA"

        # --- ESTADO 2: BUSCAR LINEA ---
        elif estado_carrera == "BUSCAR_LINEA":
            # Si se detecta la marca azul de esquina en el suelo (Área > 1200)
            if LNM.blue_area > 1200:
                print("🔷 [EVENTO] ¡Línea azul de esquina detectada de forma sólida!")
                estado_carrera = "LINEA_ENCONTRADA"
            else:
                # Si no la ve, sigue navegando con el PID de centrado normal
                error = black_areas[1] - black_areas[0]
                integral += error
                integral = max(-MAX_INTEGRAL, min(MAX_INTEGRAL, integral))
                derivative = error - prev_error
                correction = (Kp_vision * error) + (Ki_vision * integral) + (Kd_vision * derivative)
                prev_error = error
                
                steering_angle = int(80 + correction)
                steering_angle = max(45, min(115, steering_angle))
                
                LNM.move_forward(VELOCIDAD_BASE)
                if abs(error) < UMBRAL_PIXELES_MUERTO:
                    LNM.turn_center()
                elif steering_angle > 80:
                    LNM.turn_right(angle=steering_angle, speed=VELOCIDAD_BASE)
                elif steering_angle < 80:
                    LNM.turn_left(angle=steering_angle, speed=VELOCIDAD_BASE)

        # --- ESTADO 3: LINEA ENCONTRADA ---
        elif estado_carrera == "LINEA_ENCONTRADA":
            print("🎯 [CONFIGURACIÓN] Confirmado: Vehículo posicionado en zona de curva. Pasando a aproximación.")
            # Transición inmediata al siguiente estado para mantener el flujo continuo de ejecución
            estado_carrera = "INICIO_RETROCESO"

        # --- ESTADO 4: INICIO DE RETROCESO (APROXIMACIÓN CRÍTICA) ---
        elif estado_carrera == "INICIO_RETROCESO":
            # El carro sigue avanzando en línea recta buscando encajonarse perfectamente en la esquina
            LNM.move_forward(VELOCIDAD_BASE - 10) # Reduce ligeramente la velocidad para mayor precisión de lectura
            LNM.turn_center()
            
            # Evaluación estricta de las firmas ultrasónicas solicitadas:
            # Muy cerca de la pared frontal Y ultrasonido izquierdo > 2 metros (200 cm) Y derecho < 50 cm
            if front_dist < 18.0 and left_dist > 200.0 and right_dist < 50.0:
                print("🏁 [CONDICIONES DE ESQUINA CUMPLIDAS] Frente < 18cm | Izq > 2m | Der < 50cm.")
                LNM.stop(log=False)
                tiempo_inicio_retroceso = time.time()  # Captura el tiempo de inicio de la maniobra cronometrada
                estado_carrera = "RETROCESO"
            
            # Resguardo de seguridad: Si por alguna razón no lee correctamente y se acerca demasiado al frente, aborta
            elif front_dist < DIST_MIN_CHOQUE:
                print("⚠️ [SEGURIDAD] Proximidad frontal límite alcanzada antes de la firma exacta. Forzando retroceso.")
                LNM.stop(log=False)
                tiempo_inicio_retroceso = time.time()
                estado_carrera = "RETROCESO"

        # --- ESTADO 5: RETROCESO CRONOMETRADO FIJO ---
        elif estado_carrera == "RETROCESO":
            # Comprobación del tiempo transcurrido (3.5 segundos requeridos)
            if (time.time() - tiempo_inicio_retroceso) < 3.5:
                # Deja el servo fijo exactamente en 120 grados y retrocede con potencia controlada
                LNM.move_backward(angle=120, speed=85)
            else:
                print("✅ [MANIOBRA COMPLETADA] Centrado de esquina finalizado con éxito. Volviendo a LINEAL.")
                LNM.stop(log=False)
                LNM.turn_center(log=False)
                
                # Limpieza total de integrales y estados para arrancar la recta totalmente limpios
                prev_error = 0.0
                integral = 0.0
                LNM.vision.reset_stuck_timer()
                estado_carrera = "LINEAL"

    except Exception as e:
        print("Error crítico ejecutando el bucle de control:", e)
        break

LNM.stop()
cv2.destroyAllWindows()
