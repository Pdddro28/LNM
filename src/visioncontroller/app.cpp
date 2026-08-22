#include "vision_controller.h"
#include <iostream>

int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;

    // Al crear este objeto, se ejecuta automáticamente el constructor
    VisionController vision;
    ROI main_roi = {220, 85, 420, 285}; 

    std::cout << "VisionController creado exitosamente." << std::endl;
    std::vector<std::vector<cv::Point>> red;
    while (true){
        vision.receive_image();
        if (vision.get_frame().empty()) {
            std::cerr << "No se pudo obtener imagen" << std::endl;
            continue; // Intentar capturar la imagen nuevamente
        }
        red = vision.find_contours({{18, 157, 0}, {255, 255, 255}}, main_roi);
        vision.draw_contours(red, main_roi, cv::Scalar(0, 0, 255)); // Dibujar contornos en rojo
        vision.draw_roi(main_roi, cv::Scalar(255, 0, 0)); // Dibujar ROI de prueba
        
        cv::imshow("Frame", vision.get_frame());
        char key = (char)cv::waitKey(1);
        if (key == 'q') { // Salir si se presiona 'Esc'
            break;
        }
    }
    // El destructor se ejecuta automáticamente al llegar aquí
    return 0;
}