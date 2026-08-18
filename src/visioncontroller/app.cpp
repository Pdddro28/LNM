#include "vision_controller.h"
#include <iostream>

int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;

    // Al crear este objeto, se ejecuta automáticamente el constructor
    VisionController vision;

    std::cout << "VisionController creado exitosamente." << std::endl;

    // El destructor se ejecuta automáticamente al llegar aquí
    return 0;
}