#include "vision_controller.h"
#include <iostream>
#include <pigpio.h>
#include <chrono>
#include <thread>
#include <csignal>
#include <atomic>
#include <string>

// Pines GPIO (BCM)
const int SERVO_PIN = 18; // Hardware PWM vía DMA de pigpio
const int MOTOR_IN1 = 19; // GPIO Digital (DRV8833)
const int MOTOR_IN2 = 13; // GPIO Digital (DRV8833)
const int BUTTON_PIN = 25; // GPIO Boton


// Bandera atómica: segura para modificarse dentro de una interrupción
std::atomic<bool> ejecutando(true);
std::string ESTADO_CARRERA = "INICIANDO";

VisionController vision(CameraBackend::GSTREAMER); 

ROI roi1 = {0, 40, 320, 160}; // ROI lateral izquierdo
ROI roi2 = {320, 40, 640, 160}; // ROI lateral derecho
ROI roi3 = {200, 20, 430, 200}; // ROI central
ROI roi4 = {200, 90, 430, 200}; // ROI inferior
ROI roi5 = {200, 70, 430, 140}; // ROI superior naranja

enum class Sentido { PARAR, ADELANTE, ATRAS };

// CORRECCIÓN 1: Función de interrupción asíncrona sin operaciones de I/O (std::cout eliminado)
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

int get_color_area(ROI roi, const cv::Mat& frame, const std::vector<std::vector<int>>& range_colors) {
    if (frame.empty()) return 0;
    cv::Mat roi_frame = frame(cv::Rect(roi.x1, roi.y1, roi.x2 - roi.x1, roi.y2 - roi.y1));
    
    auto color_contours = vision.find_contours(range_colors, roi);
    auto max_contour_result = vision.max_contour(color_contours, roi);
    
    if (max_contour_result.empty()) return 0;
    return max_contour_result[0].first;
}

// Color Detector
int left_blk = 0;
int right_blk = 0;
int central_blk = 0;
int down_blue = 0;
int down_orange = 0;
int central_orange = 0;
int central_blkt = 0;

// Others
int turning_direction = 0;
int frame_count = 0;
int loops = 0;
int n = 0;
int transicion = 0;

// Cronometro

double obtener_tiempo_actual() {
    auto ahora = std::chrono::steady_clock::now();
    return std::chrono::duration<double>(ahora.time_since_epoch()).count();
}

// Variables de cronómetro
double current_timer = 0.0;
double stop_timer = 0.0;

// Variable global o static para el tiempo de inicio de giro
double tiempo_inicio_giro = 0.0;

// Booleans
bool stop_triggered = false; // Bandera para activar el cronómetro de la vuelta 12 una sola vez

// PID
float error;
float correccion;
float kp;
float angulo;


int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;
    std::cout << "VisionController creado exitosamente." << std::endl;
    
    const std::vector<std::vector<int>> range_black = {{0, 0, 100}, {85, 255, 255}};
    const std::vector<std::vector<int>> range_blue  = {{0, 0, 0}, {180, 180, 110}};
    const std::vector<std::vector<int>> range_orange = {{50, 100, 145}, {255, 255, 255}};

    // Inicializar el motor DMA de pigpio
    if (gpioInitialise() < 0) {
        std::cerr << "❌ Error inicializando pigpio. Ejecuta con sudo.\n";
        return -1;
    }

    // CORRECCIÓN 2: Uso del gestor de señales nativo de pigpio para evitar conflictos de hilos
    gpioSetSignalFunc(SIGINT, capturar_ctrl_c);

    // Configurar pines como salidas
    gpioSetMode(SERVO_PIN, PI_OUTPUT);
    gpioSetMode(MOTOR_IN1, PI_OUTPUT);
    gpioSetMode(MOTOR_IN2, PI_OUTPUT);

    // --- CONFIGURACIÓN DEL BOTÓN ---
    gpioSetMode(BUTTON_PIN, PI_INPUT);
    gpioSetPullUpDown(BUTTON_PIN, PI_PUD_UP); // Activa resistencia pull-up interna

    // Posición inicial segura
    mover_motor(Sentido::PARAR,0);
    mover_servo(90);

    std::cout << "\n==================================================\n";
    std::cout << "🟢 HARDWARE LISTO.\n";
    std::cout << "🔘 ESPERANDO PULSACIÓN DEL BOTÓN EN GPIO " << BUTTON_PIN << "...\n";
    std::cout << "==================================================\n\n";

    // --- BUCLE DE ESPERA DEL BOTÓN ---
    while (ejecutando && gpioRead(BUTTON_PIN) == PI_LOW) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    // Si se presionó Ctrl+C durante la espera, salir limpiamente
    if (!ejecutando) {
        gpioTerminate();
        return 0;
    }

    std::cout << "🚀 ¡BOTÓN PRESIONADO! ARANCANDO EN 1 SEGUNDO...\n\n";
    pausa_segura(1000);
    
    // Ejecución del carro
    while (ejecutando) {
        current_timer = obtener_tiempo_actual();
        vision.receive_image();
        const cv::Mat& current_frame = vision.get_frame();

        if (current_frame.empty()) {
            std::cerr << "No se pudo obtener imagen" << std::endl;
            continue;
        }

        left_blk = get_color_area(roi1, current_frame, range_black);
        right_blk = get_color_area(roi2, current_frame, range_black);
        central_blk = get_color_area(roi3, current_frame, range_black);
        down_blue = get_color_area(roi4, current_frame, range_blue);
        down_orange = get_color_area(roi4, current_frame, range_orange);
        central_orange = get_color_area(roi5, current_frame, range_orange);
        central_blkt = get_color_area(roi5, current_frame, range_black);

  
        /*vision.draw_roi(roi1, cv::Scalar(255, 0, 0));
        vision.draw_roi(roi2, cv::Scalar(255, 0, 0));*/
        /*vision.draw_roi(roi3, cv::Scalar(255, 255, 0));
        vision.draw_roi(roi4, cv::Scalar(255, 0, 255));
        vision.draw_roi(roi5, cv::Scalar(255, 0, 0));*/

        // Texto con información
        std::cout << "Orange Max Area: " << down_orange << "\n"
                  << "transicion " << transicion << "\n"
                  << "Black central chiqui Max Area: " << central_blkt << "\n"
                  << "Blue Max Area: "   << down_blue   << "\n"
                  << "BlackC Max Area: " << central_blk << "\n"
                  << "BlackL Max Area: " << left_blk << "\n"
                  << "BlackR Max Area: " << right_blk << std::endl;
        
        if (turning_direction == 0) {
            if (down_orange > 1500) {
                turning_direction = 2;
                std::cout << "Area Orange" << std::endl;
            } else if (down_blue > 1500) {
                turning_direction = 1;
                std::cout << "Area Blue" << std::endl;
            }
        }

        
        if (ESTADO_CARRERA == "INICIANDO") {
            if (transicion == 1) transicion = 0;
            mover_motor(Sentido::ADELANTE, 200); //200
            error = left_blk - right_blk;
            correccion = 0.001 * error;
            angulo = 90 + correccion;
            
            if (angulo < 70) {
                angulo = 70;
            }
            else if (angulo > 110) {
                angulo = 110;
            }
            
            mover_servo((int)angulo);
            
            
            if (down_orange > 500 && turning_direction == 2) {
                ESTADO_CARRERA = "GIRANDO";
            } else if (turning_direction == 1 && central_blkt > 200 && central_blkt < 1500){
                ESTADO_CARRERA = "GIRANDO";

            }

        } else if (ESTADO_CARRERA == "GIRANDO") {
            if (turning_direction == 2){
                mover_motor(Sentido::ADELANTE, 140); //150
                mover_servo(110);
            }    
            else if (turning_direction == 1){
                mover_motor(Sentido::ADELANTE, 120); //130
                mover_servo(80);
                
            }
            
            if (turning_direction == 2 && central_blk < 8000) {
                ESTADO_CARRERA = "INICIANDO";
            }
            if (turning_direction == 1 && (central_blk < 8400  || central_blkt > 5000)){
                ESTADO_CARRERA = "INICIANDO";
            }
        }   

        std::cout << ESTADO_CARRERA << std::endl;
        std::cout << (int)angulo << std::endl;
        std::cout << loops <<std::endl;
        
        if (ESTADO_CARRERA == "GIRANDO" && transicion == 0) {
            loops++;
            transicion = 1;
        }

        // --- LÓGICA DE LOS 5 SEGUNDOS EXTRA TRAS LA VUELTA 12 ---
        if (loops >= 12 && !stop_triggered && turning_direction == 2) {
            stop_timer = current_timer; // Guarda el momento exacto en que llegó a la 12
            stop_triggered = true;      // Activa la bandera para que no se reinicie
            std::cout << "🏁 ¡Vuelta 12 alcanzada! Avanzando 5 segundos más..." << std::endl;
        }  /*else if (loops >=  && !stop_triggered && turning_direction == 2) {
            stop_timer = current_timer; // Guarda el momento exacto en que llegó a la 12
            stop_triggered = true;      // Activa la bandera para que no se reinicie
            std::cout << "🏁 ¡Vuelta 12 alcanzada! Avanzando 5 segundos más..." << std::endl;
        }td::cout << "🏁 ¡Vuelta 12 alcanzada! Avanzando 5 segundos más..." << std::endl;
        }*/
        
        // Si ya se activó el cronómetro, evaluamos si han pasado los 5.0 segundos
        if (stop_triggered) {
            if (current_timer - stop_timer >= 4.5) {
                break; // Rompe el bucle para ir al apagado seguro
            }
        }

        //pausa_segura(2000);
        /*cv::imshow("Frame", current_frame);
        char key = (char)cv::waitKey(1);   
        if (key == 'q') {
            break;        
                ESTADO_CARRERA = "GIRANDO";
        } */
    }

    // --- APAGADO SEGURO GARANTIZADO ---
    // CORRECCIÓN 3: Impresión del mensaje de aborto movido al hilo principal
    std::cout << "\n[!] Interrupción detectada. Abortando y limpiando recursos...\n";
    std::cout << "Apagando motor, cortando pulso del servo y liberando memoria...\n";
    
    mover_motor(Sentido::PARAR,0); 
    gpioServo(SERVO_PIN, 0);     
    gpioTerminate();             

    std::cout << "✅ Robot detenido y recursos liberados correctamente.\n";
    return 0;
}
