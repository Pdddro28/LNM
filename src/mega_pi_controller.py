import serial
import time
import threading
import pandas as pd
import random
from vision_controller import VisionController
import json
import cv2
from dataclasses import dataclass

# --- DATA STRUCTURES ---
@dataclass
class ROI:
    x1: int; y1: int
    x2: int; y2: int

# --- MEGAPROBOT MAIN CONTROLLER ---
class MegaPiController:

    # --- INITIALIZATION AND HARDWARE SETUP ---
    def __init__(self, port='COM9', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            time.sleep(2) 
            print(f"✅ System: Connected to MegaPi on {port}")
            
            # --- Sensores de Distancia (Actualizados a la nueva configuración) ---
            self.dist_front = 0   # Ultrasónico Frontal
            self.dist_right = 0    # Ultrasónico Izquierdo
            self.dist_left = 0    # Ultrasónico Izquierdo
            self.dist_laser1 = 0  # NUEVO: Sensor Láser ToF 1 (0x30)
            self.dist_laser2 = 0  # NUEVO: Sensor Láser ToF 2 (0x29)
            
            self.data_log = []
            self.log_index = 0
            self.vision = VisionController()  
            
            time.sleep(1)  
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_telemetry, daemon=True)
            self.reader_thread.start()
            self.button_value = 0
            self.turning_direction = 0 

            self.ACTION_LEFT = 0
            self.ACTION_FORWARD = 1
            self.ACTION_RIGHT = 2

            self.load_masks()

            self.black_area = 0
            self.black_area_derecha = 0
            self.blue_area = 0
            self.upper_orange_area = 0
            self.orange_area = 0
            self.green_area = 0
            self.red_area = 0
            
            self.rois = [
                ROI(200, 20, 430, 200),
                ROI(200, 300, 440, 350),
            ]

        except Exception as e:
            print(f"❌ Critical Error: Could not connect to {port}. {e}")
            exit()

    # --- SERIAL BACKGROUND DATA PACKET READING ---
    def _read_telemetry(self):
        while self.running:
            try:
                # Esperamos el paquete de 8 bytes (1 header + 7 datos)
                if self.ser.in_waiting >= 8:
                    header = self.ser.read(1)
                    
                    if header == b'\xaa':
                        payload = self.ser.read(7)
                        
                        # Mapeo idéntico al Serial.write() del nuevo Arduino:
                        self.dist_front   = payload[0] # Byte 1: Ultrasónico Frontal
                        self.dist_left    = payload[1] # Byte 2: Ultrasónico Izquierdo
                        self.dist_right   = payload[2]
                        self.dist_laser1  = payload[3] # Byte 3: Láser VL53L0X (1)
                        self.dist_laser2  = payload[4] # Byte 4: Láser VL53L0X (2)
                        self.button_value = payload[5] # Byte 5: Botón
                        
                        # payload[5] y payload[6] son bytes de relleno (0x00), se ignoran.
                        
                    else:
                        line = self.ser.readline().decode('ascii', errors='ignore').strip()
                        #if line:
                            #print(f"   [MegaPi Debug]: {line}")
            except Exception as e:
                print(f"Telemetry Error: {e}")
            
            time.sleep(0.01) 
    
    # --- LOW-LEVEL SERIAL COMMAND SENDING ---
    def _send_command(self, action, v1=0, v2=0):
        header = 0xFF
        msg_type = 0x01
        package = bytearray([header, msg_type, action, v1, v2])
        try:
            if hasattr(self, 'ser') and self.ser.is_open:
                self.ser.write(package)
        except serial.SerialException as e:
            print(f"⚠️ [Fallo de Enlace]: No se pudo enviar el comando {action}. {e}")

    # --- COMPUTER VISION SUBSYSTEM ---
    def get_masks(self, color):
        with open(f'src/Colors/mask_{color}.json') as f:
            config = json.load(f)
        lower = config['bounds']['lower']
        upper = config['bounds']['upper']
        return [lower, upper]

    def load_masks(self):
        self.mask_red = self.get_masks('rojo')
        self.mask_green = self.get_masks('verde')
        self.mask_blue = self.get_masks('azul')
        self.mask_orange = self.get_masks('naranja')
        self.mask_black = self.get_masks('negro')

    def obtenerarea_frontal(self):
        self.cnt_front_wall = self.vision.find_contours(self.mask_black, self.rois[0])
        self.black_area = self.vision.max_contour(self.cnt_front_wall, self.rois[0])[0]

    def obtener_linea_azul(self):
        self.cnt_blue_line = self.vision.find_contours(self.mask_blue, self.rois[1])
        self.blue_max = self.vision.max_contour(self.cnt_blue_line, self.rois[1])
        self.blue_area = self.blue_max[0]

    def obtener_linea_naranja(self):
        self.cnt_orange_line = self.vision.find_contours(self.mask_orange, self.rois[1])
        self.orange_max = self.vision.max_contour(self.cnt_orange_line, self.rois[1])
        self.orange_area = self.orange_max[0]

    def debug_UI(self):
        for item in self.rois:
            self.vision.draw_roi(item)  
        self.vision.draw_contours(self.blue_max[3], self.rois[1], (255, 255, 0))  
        self.vision.draw_contours(self.orange_max[3], self.rois[1], (0, 255, 255))  
        self.vision.draw_contours(self.cnt_front_wall, self.rois[0], (0, 0, 255))  

        cv2.imshow('Vision HD - Posicion Corregida', self.vision.frame)

    # --- TELEMETRY DATA LOGGING ---
    def log_step(self, action_code):
        d_front, d_left, d_right, d_l1, d_l2 = self.get_distances()

        self.data_log.append({
            'index': self.log_index,
            'dist_front_cm': d_front,
            'dist_left_cm': d_left,
            'dist_right_cm': d_right,
            'dist_laser1_cm': d_l1, # Guardar distancias reales del ToF
            'dist_laser2_cm': d_l2,
        })
        
        self.log_index += 1

    # --- LOCOMOTION AND STEERING HIGH-LEVEL COMMANDS ---
    def move_forward(self, speed, log=True):
        self._send_command(1, v1=speed)
        if log: self.log_step(self.ACTION_FORWARD)

    def move_backward(self, angle, speed, log = True):
        self._send_command(2, v1 = angle, v2 = speed)
        if log: self.log_step(self.ACTION_FORWARD)

    def turn_direction(self):
        if self.turning_direction == 1:
            self.turn_left(angle = 40, speed = 80, log = True) 
        elif self.turning_direction == 2:
            self.turn_left(angle = 120, speed = 80, log = True) 

    def turn_left(self, angle, speed, log = True):
        self._send_command(3, v1 = angle, v2 = speed)
        if log: self.log_step(self.ACTION_LEFT)

    def turn_right(self, angle, speed, log = True):
        self._send_command(4, v1 = angle, v2 = speed)
        if log: self.log_step(self.ACTION_RIGHT)

    def turn_center(self, log = True):
        self._send_command(6)
        if log: self.log_step(self.ACTION_FORWARD)

    def stop(self, log = True):
        self._send_command(5)

    # REVISADO: Retorna los 4 sensores activos actuales
    def get_distances(self):
        return (self.dist_front, self.dist_left, self.dist_right, self.dist_laser1, self.dist_laser2)

    def start(self):
        return self.button_value == 1

    # --- SYSTEM EXITS AND RESOURCE MANAGEMENT ---
    def save_data_to_csv(self, filename = 'training_data.csv'):
        if not self.data_log:
            print("⚠️ No data collected to save.")
            return

        try:
            df = pd.DataFrame(self.data_log)
            df.set_index('index', inplace = True)
            df.to_csv(filename, index=True)
            print(f"\n✅ Success: Saved {len(df)} records to '{filename}'")
            print(df.head())
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")

    def close(self):
        self.running = False
        self.stop(log = False)
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()

if __name__ == "__main__":
    LNM = MegaPiController("/dev/ttyUSB0", 115200)
    LNM.turn_left(120,60)
    time.sleep(0.5)
    LNM.turn_center()
    