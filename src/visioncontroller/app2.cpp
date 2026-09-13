#include "vision_controller.h"
#include <iostream>
#include <pigpio.h>
#include <chrono>
#include <thread>
#include <csignal>
#include <atomic>
#include <string>
#include <cmath>

// Pines GPIO (BCM)
const int SERVO_PIN = 18; // Hardware PWM vía DMA de pigpio
const int MOTOR_IN1 = 19; // GPIO Digital (DRV8833)
const int MOTOR_IN2 = 13; // GPIO Digital (DRV8833)
const int BUTTON_PIN = 25; // GPIO Boton

// Bandera atómica: segura para modificarse dentro de una interrupción
std::atomic<bool> ejecutando(true);

VisionController vision(CameraBackend::GSTREAMER); 

ROI roi1 = {0, 40, 320, 160}; // ROI lateral izquierdo
ROI roi2 = {320, 40, 640, 160}; // ROI lateral derecho
ROI roi3 = {200, 20, 430, 200}; // ROI central
ROI roi4 = {200, 90, 430, 200}; // ROI inferior
ROI roi5 = {200, 70, 430, 140}; // ROI superior naranja
ROI roi6 = {10, 50, 630, 300}; // ROI superior general

enum class Sentido { PARAR, ADELANTE, ATRAS };

// Función de interrupción asíncrona sin operaciones de I/O (std::cout eliminado)
void capturar_ctrl_c(int senal) {
    ejecutando = false;
}

// Mueve el servo en su rango real útil (500us - 2500us)
void mover_servo(int angulo) {
    if (angulo < 0) angulo = 0;
    if (angulo > 180) angulo = 180;

    int pulso_us = 500 + (angulo * 2500 / 180);
    gpioServo(SERVO_PIN, pulso_us);
}

// Estados del motor
void mover_motor(Sentido direccion, int vel) {
    if (direccion == Sentido::ADELANTE) {
        gpioPWM(MOTOR_IN1, vel);
        gpioWrite(MOTOR_IN2, PI_LOW);
    } else if (direccion == Sentido::ATRAS) {
        gpioWrite(MOTOR_IN1, PI_LOW);
        gpioPWM(MOTOR_IN2, vel);
    } else { // PARAR (freno / desconexión)
        gpioWrite(MOTOR_IN1, PI_LOW);
        gpioWrite(MOTOR_IN2, PI_LOW);
    }
}

// Pausa que responde al instante si se presiona Ctrl + C
void pausa_segura(int milisegundos) {
    int pasos = milisegundos / 50;
    for (int i = 0; i < pasos && ejecutando; ++i) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
}

// Cronometro
std::chrono::steady_clock::time_point LastTimeDetected;

std::vector<std::pair<int, cv::Mat>> get_color_area(ROI roi, const cv::Mat& frame, const std::vector<std::vector<int>>& range_colors) {
    if (frame.empty()) return {};
    cv::Mat roi_frame = frame(cv::Rect(roi.x1, roi.y1, roi.x2 - roi.x1, roi.y2 - roi.y1));
    
    auto color_contours = vision.find_contours(range_colors, roi);
    auto max_contour_result = vision.max_contour(color_contours, roi);
    
    if (max_contour_result.empty()) return {};
    return max_contour_result;
}

// Color Detector
int left_blk = 0;
int right_blk = 0;
int central_blk = 0;
int down_blue = 0;
int down_orange = 0;
int central_orange = 0;
int central_blkt = 0;
int central_red_area = 0;
int central_red_X = 0;
int central_green_area = 0;
int central_green_X = 0;

std::vector<std::pair<int, cv::Mat>> red_data;
std::vector<std::pair<int, cv::Mat>> green_data;

// Others
int turning_direction = 0;
int frame_count = 0;
int loops = 0;
int transicion = 0;

// SetPoint

int set_point_red = 60;
int set_point_green = 584;

// Angulos

int angulo_centro = 90;
int angulo_min = 70;
int angulo_max = 115;
int angulo_servo = angulo_centro;

// Kp
float kp = 0.007f;
float kp_red = 0.4f;
float kp_green = 0.01f;

// Kd
float kd = 0.02f;
float kd_green = 0.0;
float kd_red = 0.15;

// Previous errors
float previous_error = 0.0;
float previous_error_green = 0.0;
float previous_error_red = 0.0;

// Variables de cronómetro
double current_timer = 0.0;
double stop_timer = 0.0;

// Booleans
bool stop_triggered = false; // Bandera para activar el cronómetro de la vuelta 12 una sola vez
bool CDloops = false;

// PID
float absolute_error;

// --- VARIABLES DE HISTÉRESIS PARA OBSTÁCULOS (AGREGAR ESTO) ---
bool modo_esquive_activo = false;
int frames_sin_obstaculo = 0;
int frames_en_esquive = 0;
const int FRAMES_ESPERA_SALIDA = 8;   // ~0.3 a 0.4 segundos de "memoria"
const int FRAMES_MIN_ESQUIVE = 8;     // Frames mínimos que debe durar el esquive
bool ultimo_obstaculo_fue_rojo = false; // Para recordar el color si parpadea


// Main code

int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;
    std::cout << "VisionController creado exitosamente." << std::endl;
    
    const std::vector<std::vector<int>> range_black = {{0, 0, 100}, {85, 255, 255}};
    const std::vector<std::vector<int>> range_blue  = {{0, 0, 0}, {180, 180, 110}};
    const std::vector<std::vector<int>> range_orange = {{100, 100, 155}, {190, 170, 255}};
    const std::vector<std::vector<int>> range_red = {{0, 170, 145}, {145, 255, 180}};
    const std::vector<std::vector<int>> range_green = {{90, 75, 155}, {255, 125, 180}};
    const std::vector<std::vector<int>> range_purple = {{34, 161, 87}, {255, 255, 127}};

    // Inicializar el motor DMA de pigpio
    if (gpioInitialise() < 0) {
        std::cerr << "❌ Error inicializando pigpio. Ejecuta con sudo.\n";
        return -1;
    }

    // Uso del gestor de señales nativo de pigpio para evitar conflictos de hilos
    gpioSetSignalFunc(SIGINT, capturar_ctrl_c);

    // Configurar pines como salidas
    gpioSetMode(SERVO_PIN, PI_OUTPUT);
    gpioSetMode(MOTOR_IN1, PI_OUTPUT);
    gpioSetMode(MOTOR_IN2, PI_OUTPUT);

    // CONFIGURACIÓN DEL BOTÓN
    gpioSetMode(BUTTON_PIN, PI_INPUT);
    gpioSetPullUpDown(BUTTON_PIN, PI_PUD_UP); // Activa resistencia pull-up interna

    // Posición inicial segura
    mover_motor(Sentido::PARAR, 0);
    mover_servo(90);

    std::cout << "\n==================================================\n";
    std::cout << "🟢 HARDWARE LISTO.\n";
    std::cout << "🔘 ESPERANDO PULSACIÓN DEL BOTÓN EN GPIO " << BUTTON_PIN << "...\n";
    std::cout << "==================================================\n\n";

    // BUCLE DE ESPERA DEL BOTÓN
    while (ejecutando && gpioRead(BUTTON_PIN) == PI_LOW) { // ACTIVACION/DESACTIVACION 
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    // Si se presionó Ctrl+C durante la espera, salir limpiamente
    if (!ejecutando) {
        gpioTerminate();
        return 0;
    }
    
    // Main code
    while (ejecutando) {
        vision.receive_image();
        const cv::Mat& current_frame = vision.get_frame();

        if (current_frame.empty()) {
            std::cerr << "No se pudo obtener imagen" << std::endl;
            continue;
        }

        // Cronometro

        auto now = std::chrono::steady_clock::now();

        if (CDloops) {
            std::chrono::duration<double> transcurrido = now - LastTimeDetected;

            if (transcurrido.count() >= 1.0) {
                CDloops = false;
            }
        }

        auto res_left = get_color_area(roi1, current_frame, range_black);
        left_blk = !res_left.empty() ? res_left[0].first : 0;

        auto res_right = get_color_area(roi2, current_frame, range_black);
        right_blk = !res_right.empty() ? res_right[0].first : 0;

        auto res_central = get_color_area(roi3, current_frame, range_black);
        central_blk = !res_central.empty() ? res_central[0].first : 0;

        auto res_blue = get_color_area(roi4, current_frame, range_blue);
        down_blue = !res_blue.empty() ? res_blue[0].first : 0;

        auto res_orange = get_color_area(roi4, current_frame, range_orange);
        down_orange = res_orange[0].first;

        auto res_blkt = get_color_area(roi5, current_frame, range_black);
        central_blkt = !res_blkt.empty() ? res_blkt[0].first : 0;

        red_data = get_color_area(roi6, current_frame, range_red);
        green_data = get_color_area(roi6, current_frame, range_green);

        central_red_area = !red_data.empty() ? red_data[0].first : 0;
        central_red_X    = red_data.size() > 1 ? red_data[1].first : 0;

        central_green_area = !green_data.empty() ? green_data[0].first : 0;
        central_green_X    = green_data.size() > 1 ? green_data[1].first : 0;
        
        // --- VARIABLES DE HISTÉRESIS PARA OBSTÁCULOS --- bool modo_esquive_activo = false; int frames_sin_obstaculo = 0; int frames_en_esquive = 0; const int FRAMES_ESPERA_SALIDA = 8;   // ~0.3 a 0.4 segundos de "memoria" const int FRAMES_MIN_ESQUIVE = 5;     // Frames mínimos que debe durar el esquive bool ultimo_obstaculo_fue_rojo = false; // Para recordar el color si parpadea
        bool hay_obstaculo_rojo = (central_red_area > 900 && central_red_area > central_green_area);
        bool hay_obstaculo_verde = (central_green_area > 2200 && central_green_area > central_red_area);
        bool hay_obstaculo = hay_obstaculo_rojo || hay_obstaculo_verde;

        if (hay_obstaculo) {
            frames_sin_obstaculo = 0;                  // Reset: lo estamos viendo
            modo_esquive_activo = true;
            frames_en_esquive++;
            
            // Guardamos en memoria qué color vimos (evita que cambie a mitad del esquive)
            if (hay_obstaculo_rojo) {
                ultimo_obstaculo_fue_rojo = true;
            } else {
                ultimo_obstaculo_fue_rojo = false;
            }
        } else {
            frames_sin_obstaculo++;                    // No lo vemos, sumamos 1 frame
        }

        // ¿Ya podemos salir del modo esquive?
        if (frames_sin_obstaculo >= FRAMES_ESPERA_SALIDA) {
            modo_esquive_activo = false;
            frames_en_esquive = 0; // Reiniciamos para la próxima vez
        }

        /*vision.draw_roi(roi1, cv::Scalar(255, 0, 0));
        vision.draw_roi(roi2, cv::Scalar(255, 0, 0));*/
        /*vision.draw_roi(roi3, cv::Scalar(255, 255, 0));
        vision.draw_roi(roi4, cv::Scalar(255, 0, 255));
        vision.draw_roi(roi5, cv::Scalar(255, 0, 0));*/

        // Texto con información
        std::cout//<< "Blue Max Area: "   << down_blue   << "\n"
                 //<< "Orange Max Area: " << down_orange << "\n"
                 << "Red Area: " << central_red_area << " | X: " << central_red_X <<  "\n"
                 << "Green Area: " << central_green_area << " | X: " << central_green_X << "\n"
                 //<< "Transicion " << transicion << "\n"
                 << "Error abs: " << absolute_error << "\n"
                 << "Previous Error: " << previous_error << "\n"
                 << "BlackC Max Area: " << central_blk << "\n"
                 << "BlackL Max Area: " << left_blk << "\n"
                 << "BlackR Max Area: " << right_blk << std::endl;


        // =========================================================================
        // LÓGICA DE ESQUIVE CON PESO POR PROXIMIDAD (ÁREA)
        // =========================================================================
        if (modo_esquive_activo) {
            
            if (ultimo_obstaculo_fue_rojo) {
                float error_red = central_red_X - set_point_red;
                float derivative_red = error_red - previous_error_red;
                previous_error_red = error_red;
                
                // 1. CALCULAR PESO POR PROXIMIDAD (ROJO)
                // Restamos el umbral de detección (900). Si está lejos, area_util es 0.
                float area_util = std::max(0.0f, (float)central_red_area - 900.0f);
                // Dividimos por 2500. Cuando el área sea 3400, el peso será 1.0 (100% de corrección)
                float peso = std::min(1.0f, area_util / 2500.0f);
                
                // 2. APLICAR EL PESO A LA CORRECCIÓN TOTAL
                float correccion_der = peso * ((kp_red * error_red) + (kd_red * derivative_red));
                float angulo_red = angulo_centro + correccion_der;
    
                if (angulo_red < 80) angulo_red = 80;
                else if (angulo_red > 110) angulo_red = 110;
                
                // 3. VELOCIDAD ADAPTATIVA: Frena suavemente mientras más cerca esté el obstáculo
                int velocidad = 200 - (int)(peso * 60); // Rango: 200 (lejos) a 140 (muy cerca)
                
                mover_servo((int)angulo_red);
                mover_motor(Sentido::ADELANTE, velocidad); 
                std::cout << "🔴 ROJO | Area: " << central_red_area << " | Peso: " << peso << " | Ang: " << (int)angulo_red << " | Vel: " << velocidad << "\n";
    
            } else {
                float error_green = central_green_X - set_point_green;
                float derivative_green = error_green - previous_error_green;
                previous_error_green = error_green;
                
                // 1. CALCULAR PESO POR PROXIMIDAD (VERDE)
                float area_util = std::max(0.0f, (float)central_green_area - 2200.0f);
                float peso = std::min(1.0f, area_util / 2500.0f);
                
                // 2. APLICAR EL PESO A LA CORRECCIÓN TOTAL
                float correccion_izq = peso * ((kp_green * error_green) + (kd_green * derivative_green));
                float angulo_green = angulo_centro + correccion_izq;
    
                if (angulo_green < 80) angulo_green = 80;
                else if (angulo_green > 110) angulo_green = 110;
                
                // 3. VELOCIDAD ADAPTATIVA
                int velocidad = 200 - (int)(peso * 60);
                
                mover_servo((int)angulo_green);
                mover_motor(Sentido::ADELANTE, velocidad); 
                std::cout << "🟢 VERDE | Area: " << central_green_area << " | Peso: " << peso << " | Ang: " << (int)angulo_green << " | Vel: " << velocidad << "\n";
            }
        } else {
            // --- LÓGICA DE PARED NEGRA (NORMAL) ---
            mover_motor(Sentido::ADELANTE, 200);
            float error = left_blk - right_blk;
            float derivative = error - previous_error;
            previous_error = error;
            float correccion = (kp * error) + (kd * derivative);
            float angulo = 90 + correccion;
            absolute_error = std::abs(error);
                
            if (angulo < 80) {
                angulo = 80;
            } else if (angulo > 110) {
                angulo = 110;
            }
                
            mover_servo((int)angulo);   
        }
        
        std::cout << "Frames sin obstaculo: " << frames_sin_obstaculo << " | Loops: " << loops << std::endl;
        std::cout << loops << std::endl;

        /*if (down_orange > 100 && turning_direction == 2 && !CDloops) {
            loops++;
            LastTimeDetected = now;
            CDloops = true;
        }

        if (down_blue > 100 && turning_direction == 1 && !CDloops) {
            loops++;
            LastTimeDetected = now;
            CDloops = true;
        }

        // PARADA 12 VUELTAS
        if (loops == 12 && !stop_triggered) {
            stop_timer = current_timer;
            stop_triggered = true;
            std::cout << "🏁 ¡Vuelta 12 alcanzada!" << std::endl;
        }
        
        if (stop_triggered) {
            if (current_timer - stop_timer >= 4.0) {
                break;
            }
        }*/
    }

    // APAGADO SEGURO GARANTIZADO
    std::cout << "\n[!] Interrupción detectada. Abortando y limpiando recursos...\n";
    std::cout << "Apagando motor, cortando pulso del servo y liberando memoria...\n";
    
    mover_motor(Sentido::PARAR, 0); 
    gpioServo(SERVO_PIN, 0);     
    gpioTerminate();             

    std::cout << "✅ Robot detenido y recursos liberados correctamente.\n";
    return 0;
}
