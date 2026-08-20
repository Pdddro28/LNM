#include "vision_controller.h"
#include <iostream>

int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;

    // Al crear este objeto, se ejecuta automáticamente el constructor
    VisionController vision;
    ROI main_roi = {220, 85, 420, 285}; 

    std::cout << "VisionController creado exitosamente." << std::endl;
    while (true){
        vision.receive_image();
        if (vision.get_frame().empty()) {
            std::cerr << "No se pudo obtener imagen" << std::endl;
            continue; // Intentar capturar la imagen nuevamente
        }

        vision.draw_roi(main_roi, cv::Scalar(255, 0, 0)); // Dibujar ROI de prueba
        cv::imshow("Frame", vision.get_frame());
        if (cv::waitKey(1) == 27) { // Salir si se presiona 'Esc'
            break;
        }
    }
    // El destructor se ejecuta automáticamente al llegar aquí
    return 0;
}