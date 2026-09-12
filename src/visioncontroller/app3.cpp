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

// Error

int error_green = 0;
int error_red = 0;

// Angulos

int angulo_centro = 90;
int angulo_min = 70;
int angulo_max = 115;
int angulo_servo = angulo_centro;

// Kp

float kp = 0.001f;
float kp_red = 0.11f;
float kp_green = 0.05f;

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
float angulo;
float angulo_green;

int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;
    std::cout << "VisionController creado exitosamente." << std::endl;
    
    const std::vector<std::vector<int>> range_black = {{0, 0, 100}, {85, 255, 255}};
    const std::vector<std::vector<int>> range_blue  = {{0, 0, 0}, {180, 180, 110}};
    const std::vector<std::vector<int>> range_orange = {{100, 100, 155}, {190, 170, 255}};
    const std::vector<std::vector<int>> range_red = {{0, 158, 124}, {141, 255, 167}};
    const std::vector<std::vector<int>> range_green = {{90, 75, 155}, {255, 125, 180}};

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
    while (ejecutando && gpioRead(BUTTON_PIN) == PI_HIGH) { // ACTIVACION/DESACTIVACION 
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    //mover_motor(Sentido::ADELANTE, 140); //150
    // Si se presionó Ctrl+C durante la espera, salir limpiamente
    if (!ejecutando) {
        gpioTerminate();
        return 0;
    }
    
    // Ejecución del carro
    while (ejecutando) {
        current_timer = obtener_tiempo_actual();
        vision.receive_image();
        const cv::Mat& current_frame = vision.get_frame();

        if (current_frame.empty()) {
            std::cerr << "No se pudo obtener imagen" << std::endl;
            continue;
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
        
        /*vision.draw_roi(roi1, cv::Scalar(255, 0, 0));
        vision.draw_roi(roi2, cv::Scalar(255, 0, 0));*/
        /*vision.draw_roi(roi3, cv::Scalar(255, 255, 0));
        vision.draw_roi(roi4, cv::Scalar(255, 0, 255));
        vision.draw_roi(roi5, cv::Scalar(255, 0, 0));*/

        // Texto con información
         std::cout<< "Blue Max Area: "   << down_blue   << "\n"
                  << "Red Area: " << central_red_area << " | X: " << central_red_X <<  "\n"
                  << "Green Area: " << central_green_area << " | X: " << central_green_X << "\n"
                  //<< "Transicion " << transicion << "\n"
                  << "Black central chiqui Max Area: " << central_blkt << "\n"
                  << "BlackC Max Area: " << central_blk << "\n"
                  << "BlackL Max Area: " << left_blk << "\n"
                  << "Orange Max Area: " << down_orange << "\n"
                  << "BlackR Max Area: " << right_blk << std::endl;
        
        if (turning_direction == 0) {
            if (down_orange > 100) {
                turning_direction = 2;
                //mover_motor(Sentido::ATRAS, 150);
                //mover_servo(80);
                //pausa_segura(1500);
                std::cout << "Area Orange" << std::endl;
            } else if (down_blue > 100) {
                turning_direction = 1;
                std::cout << "Area Blue" << std::endl;
            }
        }
        
        if (ESTADO_CARRERA == "INICIANDO") {
            if (transicion == 1) transicion = 0;
            mover_motor(Sentido::ADELANTE, 200);
            error = left_blk - right_blk;
            correccion = kp * error;
            angulo = 90 + correccion;
            
            if (angulo < 70) {
                angulo = 70;
            } else if (angulo > 110) {
                angulo = 110;
            }
            
            mover_servo((int)angulo);

            /*if (central_green_area > 900 && central_green_area > central_red_area) {
                ESTADO_CARRERA = "OBSTACULO_GREEN";

            } else if (central_red_area > 900 && central_red_area > central_green_area ){
                ESTADO_CARRERA = "OBSTACULO_RED";

            } else if (turning_direction == 2 && central_blk > 6000 && central_green_area == 0 && central_red_area == 0) {
                ESTADO_CARRERA = "GIRANDO";

            } else if (turning_direction == 1 && central_blk > 6000 && central_green_area == 0 && central_red_area == 0) {
                ESTADO_CARRERA = "GIRANDO";
            }*/

        } else if (ESTADO_CARRERA == "GIRANDO") {
            if (turning_direction == 2){
                mover_motor(Sentido::ADELANTE, 140);
                mover_servo(110);

            } else if (turning_direction == 1) {
                mover_motor(Sentido::ADELANTE, 120);
                mover_servo(80);
            }
            
            if (turning_direction == 2 && central_blk < 8000) {
                ESTADO_CARRERA = "INICIANDO";
            }

            if (turning_direction == 1 && central_blk < 8000 ) {
                ESTADO_CARRERA = "INICIANDO";
            }

        } else if (ESTADO_CARRERA == "OBSTACULO_RED") {
            error_red =  central_red_X - set_point_red;
            float correccion_der = kp_red * error_red;
            float angulo_red = angulo_centro + correccion_der;

            if (angulo_red < 70) {
                angulo_red = 70;
            } else if (angulo_red > 110) {
                angulo_red = 110;
            }
            mover_servo((int)angulo_red);

            if (central_red_area < 70 || central_green_area > central_red_area) {
                ESTADO_CARRERA = "INICIANDO";
            }
            std::cout << "ANGULO ROJO = "  << (int)angulo_red << std::endl;

        } else if (ESTADO_CARRERA == "OBSTACULO_GREEN") {
            error_green =  central_green_X - set_point_green;
            float correccion_izq = kp_green * error_green;
            
            
            if (central_green_X > 0) {
                angulo_green = angulo_centro + correccion_izq;

                if (angulo_green < 70) {
                    angulo_green = 70;
                } else if (angulo_green > 110) {
                    angulo_green = 110;
                }

                mover_servo((int)angulo_green);
            }

            if (central_red_area < 70 && central_green_area > central_red_area) {
                ESTADO_CARRERA = "INICIANDO";
            }

            std::cout << "ANGULO VERDE = "  << (int)angulo_green << std::endl;
        }

        std::cout << ESTADO_CARRERA << std::endl;
        std::cout << loops <<std::endl;
        
        //if (ESTADO_CARRERA == "GIRANDO" && transicion == 0) {
        //    loops++;
        //    transicion = 1;
        //}

        // PARADA 12 VUELTAS
        //if (loops == 12 && !stop_triggered) {
        //    stop_timer = current_timer; // Guarda el momento exacto en que llegó a la 12
        //    stop_triggered = true;      // Activa la bandera para que no se reinicie
        //    std::cout << "🏁 ¡Vuelta 12 alcanzada!" << std::endl;
        //}
        
        // Si ya se activó el cronómetro, evaluamos si han pasado los 5.0 segundos
        //if (stop_triggered) {
        //    if (current_timer - stop_timer >= 4.5) {
        //        break; // Rompe el bucle para ir al apagado seguro
        //    }
        //}

        /*cv::imshow("Frame", current_frame);
        char key = (char)cv::waitKey(1);   
        if (key == 'q') {
            break;        
        }*/
    }

    // APAGADO SEGURO GARANTIZADO
    // Impresión del mensaje de aborto movido al hilo principal
    std::cout << "\n[!] Interrupción detectada. Abortando y limpiando recursos...\n";
    std::cout << "Apagando motor, cortando pulso del servo y liberando memoria...\n";
    
    mover_motor(Sentido::PARAR,0); 
    gpioServo(SERVO_PIN, 0);     
    gpioTerminate();             

    std::cout << "✅ Robot detenido y recursos liberados correctamente.\n";
    return 0;
}
