#include "vision_controller.h"
#include <iostream>

int main() {
    std::cout << "=== PRUEBA DEL CONSTRUCTOR ===" << std::endl;
    std::cout << "A punto de crear VisionController..." << std::endl;

    VisionController vision;
    ROI main_roi = {220, 85, 420, 285}; 

    std::cout << "VisionController creado exitosamente." << std::endl;
    
    std::vector<std::vector<cv::Point>> red;
    std::vector<std::pair<int, cv::Mat>> max_contour_result;
    
    int frame_count = 0;
    
    while (true) {
        vision.receive_image();
        
        if (vision.get_frame().empty()) {
            std::cerr << "No se pudo obtener imagen" << std::endl;
            continue;
        }
        
        // Llamar find_contours con la firma original
        red = vision.find_contours({{18, 157, 0}, {255, 255, 255}}, main_roi);
        max_contour_result = vision.max_contour(red, main_roi);

        vision.draw_contours(red, main_roi, cv::Scalar(0, 0, 255));
        vision.draw_roi(main_roi, cv::Scalar(255, 0, 0));
        
        // Texto con información
        cv::putText(vision.get_frame(), 
                    "Max Area: " + std::to_string(max_contour_result[0].first), 
                    cv::Point(10, 30), 
                    cv::FONT_HERSHEY_SIMPLEX, 
                    1, 
                    cv::Scalar(255, 255, 255), 
                    2);
        
        // Monitoreo de RAM cada 60 frames
        if (++frame_count % 60 == 0) {
            std::cout << "RAM: " << vision.get_memory_usage_kb() / 1024.0 
                      << " MB | Contornos: " << red.size() 
                      << " | MaxArea: " << max_contour_result[0].first 
                      << std::endl;
        }
        
        //cv::imshow("Frame", vision.get_frame());
        
        char key = (char)cv::waitKey(1);
        if (key == 'q') {
            break;
        }
    }
    
    return 0;
}