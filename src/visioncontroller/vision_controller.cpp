// vision_controller.cpp
#include "vision_controller.h"

// ============================================
// CONSTRUCTOR Y DESTRUCTOR
// ============================================

VisionController::VisionController() {
    // Inicializar variables miembro
    image_width = 640;
    image_height = 370;
    
    // Configurar cámara con V4L2
    camera.open(0, cv::CAP_V4L2);
    camera.set(cv::CAP_PROP_FRAME_WIDTH, image_width);
    camera.set(cv::CAP_PROP_FRAME_HEIGHT, image_height);
    camera.set(cv::CAP_PROP_FPS, 32);
    
    // Verificar que la cámara se abrió correctamente
    if (!camera.isOpened()) {
        std::cerr << "Error: No se pudo abrir la cámara" << std::endl;
        return;
    }
    
    // Pequeña pausa para inicialización
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}

VisionController::~VisionController() {
    // Liberar recursos de la cámara
    if (camera.isOpened()) {
        camera.release();
    }
}

// ============================================
// IMAGE ACQUISITION AND PROCESSING
// ============================================

void VisionController::receive_image() {
    // Capturar frame de la cámara
    camera.read(frame);
    
    // Verificar que el frame no está vacío
    if (frame.empty()) {
        std::cerr << "No se pudo obtener imagen" << std::endl;
        return;
    }
    
    // Aplicar flip vertical y horizontal
    //cv::flip(frame, frame, 0);  // 0 = flip vertical
    //cv::flip(frame, frame, 1);  // 1 = flip horizontal
    
    // Convertir a espacio de color LAB
    cv::cvtColor(frame, image_lab, cv::COLOR_BGR2Lab);
    
    // Separar canales L, A, B
    std::vector<cv::Mat> lab_channels;
    cv::split(image_lab, lab_channels);
    
    // Aplicar CLAHE al canal L
    cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(3.0, cv::Size(8, 8));
    clahe->apply(lab_channels[0], lab_channels[0]);
    
    // Unir canales de nuevo
    cv::merge(lab_channels, image_lab);
    
    // Aplicar Gaussian Blur
    cv::GaussianBlur(image_lab, image_lab, cv::Size(7, 7), 0);
}

// ============================================
// DRAWING UTILITIES
// ============================================

void VisionController::draw_roi(const ROI& roi, const cv::Scalar& color) {
    // Dibujar rectángulo en el frame
    cv::rectangle(frame, 
                   cv::Point(roi.x1, roi.y1), 
                   cv::Point(roi.x2, roi.y2), 
                   color, 2);
}

void VisionController::draw_contours(const std::vector<std::vector<cv::Point>>& cnt, 
                                     const ROI& roi, 
                                     const cv::Scalar& color) {
    // Extraer región ROI del frame
    cv::Mat roi_region = frame(cv::Rect(roi.x1, roi.y1, 
                                          roi.x2 - roi.x1, 
                                          roi.y2 - roi.y1));
    
    // Dibujar contornos en la región ROI
    cv::drawContours(roi_region, cnt, -1, color, 2);
}

// ============================================
// COMPUTER VISION ALGORITHMS
// ============================================

std::vector<std::vector<cv::Point>> VisionController::find_contours(
    const std::vector<std::vector<int>>& range_colors, 
    const ROI& roi) {
    
    // TODO: Extraer región ROI de image_lab
    // cv::Mat img_segmented = image_lab(cv::Rect(roi.x1, roi.y1, 
    //                                             roi.x2 - roi.x1, 
    //                                             roi.y2 - roi.y1));
    
    // TODO: Crear máscaras de color inferior y superior
    // cv::Scalar lower_mask(range_colors[0][0], range_colors[0][1], range_colors[0][2]);
    // cv::Scalar upper_mask(range_colors[1][0], range_colors[1][1], range_colors[1][2]);
    
    // TODO: Aplicar filtro de rango de color
    // cv::Mat mask;
    // cv::inRange(img_segmented, lower_mask, upper_mask, mask);
    
    // TODO: Crear kernel para operaciones morfológicas
    // cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(5, 5));
    
    // TODO: Aplicar cierre morfológico
    // cv::morphologyEx(mask, mask, cv::MORPH_CLOSE, kernel);
    
    // TODO: Aplicar apertura morfológica
    // cv::morphologyEx(mask, mask, cv::MORPH_OPEN, kernel);
    
    // TODO: Encontrar contornos
    // std::vector<std::vector<cv::Point>> contours;
    // cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    
    // TODO: Retornar contornos
    // return contours;
    
    return std::vector<std::vector<cv::Point>>();
}

std::vector<std::pair<int, cv::Mat>> VisionController::max_contour(
    const std::vector<std::vector<cv::Point>>& contours, 
    const ROI& roi) {
    
    // TODO: Inicializar variables de seguimiento
    // double max_area = 0;
    // int max_x = 0, max_y = 0;
    // cv::Mat max_cnt;
    
    // TODO: Iterar sobre todos los contornos
    // for (const auto& c : contours) {
    //     double area = cv::contourArea(c);
    //     
    //     if (area > 100) {  // Umbral mínimo de área
    //         // TODO: Aproximación de polígono
    //         std::vector<cv::Point> approx;
    //         cv::approxPolyDP(c, approx, 0.01 * cv::arcLength(c, true), true);
    //         
    //         // TODO: Obtener rectángulo delimitador
    //         cv::Rect bounding_box = cv::boundingRect(approx);
    //         int x = bounding_box.x + roi.x1 + bounding_box.width / 2;
    //         int y = bounding_box.y + roi.y1 + bounding_box.height / 2;
    //         
    //         // TODO: Actualizar si es el contorno más grande
    //         if (area > max_area) {
    //             max_area = area;
    //             max_x = x;
    //             max_y = y;
    //             max_cnt = cv::Mat(c);
    //         }
    //     }
    // }
    
    // TODO: Retornar resultado como vector de pairs
    // std::vector<std::pair<int, cv::Mat>> result;
    // result.push_back(std::make_pair(static_cast<int>(max_area), max_cnt));
    // result.push_back(std::make_pair(max_x, max_cnt));
    // result.push_back(std::make_pair(max_y, max_cnt));
    // return result;
    
    return std::vector<std::pair<int, cv::Mat>>();
}