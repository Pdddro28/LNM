#include "vision_controller.h"
#include <fstream>
#include <string>

// ============================================
// CONSTRUCTOR Y DESTRUCTOR
// ============================================

VisionController::VisionController(CameraBackend backend) 
    : image_width(640), image_height(370), backend_type(backend) {
    
    // ✅ Configurar pipeline según el backend seleccionado
    if (backend_type == CameraBackend::GSTREAMER) {
        // Pipeline para Raspberry Pi con libcamera
        gstreamer_pipeline = "libcamerasrc ! "
                            "video/x-raw, width=" + std::to_string(image_width) + 
                            ", height=" + std::to_string(image_height) + 
                            ", framerate=30/1 ! "
                            "videoconvert ! video/x-raw, format=BGR ! "
                            "appsink drop=true sync=false";
        
        std::cout << "Abriendo cámara con GStreamer (libcamera)..." << std::endl;
        std::cout << "Pipeline: " << gstreamer_pipeline << std::endl;
        
        camera.open(gstreamer_pipeline, cv::CAP_GSTREAMER);
    } 
    else if (backend_type == CameraBackend::V4L2) {
        // Método tradicional V4L2
        std::cout << "Abriendo cámara con V4L2..." << std::endl;
        
        camera.open(0, cv::CAP_V4L2);
        camera.set(cv::CAP_PROP_FRAME_WIDTH, image_width);
        camera.set(cv::CAP_PROP_FRAME_HEIGHT, image_height);
        camera.set(cv::CAP_PROP_FPS, 32);
    }
    
    // Verificar que la cámara se abrió correctamente
    if (!camera.isOpened()) {
        std::cerr << "❌ Error: No se pudo abrir la cámara con el backend seleccionado." << std::endl;
        std::cerr << "Backend intentado: " 
                  << (backend_type == CameraBackend::GSTREAMER ? "GSTREAMER" : "V4L2") 
                  << std::endl;
        return;
    }
    
    std::cout << "✅ Cámara abierta correctamente con " 
              << (backend_type == CameraBackend::GSTREAMER ? "GStreamer" : "V4L2") 
              << std::endl;
    
    // Pequeña pausa para inicialización
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}

VisionController::~VisionController() {
    if (camera.isOpened()) {
        camera.release();
    }
}

// ============================================
// IMAGE ACQUISITION AND PROCESSING
// ============================================

void VisionController::receive_image() {
    camera.read(frame);
    
    if (frame.empty()) {
        std::cerr << "No se pudo obtener imagen" << std::endl;
        return;
    }
    
    cv::flip(frame, frame, 1);
    cv::flip(frame, frame, 0);

    cv::cvtColor(frame, image_lab, cv::COLOR_BGR2Lab);
    
    std::vector<cv::Mat> lab_channels;
    cv::split(image_lab, lab_channels);
    
    cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(3.0, cv::Size(8, 8));
    clahe->apply(lab_channels[0], lab_channels[0]);
    
    cv::merge(lab_channels, image_lab);
    cv::GaussianBlur(image_lab, image_lab, cv::Size(7, 7), 0);
}

// ============================================
// DRAWING UTILITIES
// ============================================

void VisionController::draw_roi(const ROI& roi, const cv::Scalar& color) {
    cv::rectangle(frame, 
                  cv::Point(roi.x1, roi.y1), 
                  cv::Point(roi.x2, roi.y2), 
                  color, 2);
}

void VisionController::draw_contours(const std::vector<std::vector<cv::Point>>& cnt, 
                                     const ROI& roi, 
                                     const cv::Scalar& color) {
    cv::Mat roi_region = frame(cv::Rect(roi.x1, roi.y1, 
                                        roi.x2 - roi.x1, 
                                        roi.y2 - roi.y1));
    cv::drawContours(roi_region, cnt, -1, color, 2);
}

// ============================================
// COMPUTER VISION ALGORITHMS
// ============================================

std::vector<std::vector<cv::Point>> VisionController::find_contours(
    const std::vector<std::vector<int>>& range_colors, 
    const ROI& roi) {
    
    cv::Mat img_segmented = image_lab(cv::Rect(roi.x1, roi.y1, 
                                               roi.x2 - roi.x1, 
                                               roi.y2 - roi.y1));
    
    cv::Scalar lower_mask(range_colors[0][0], range_colors[0][1], range_colors[0][2]);
    cv::Scalar upper_mask(range_colors[1][0], range_colors[1][1], range_colors[1][2]);
    
    cv::Mat mask;
    cv::inRange(img_segmented, lower_mask, upper_mask, mask);
    
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(5, 5));
    cv::morphologyEx(mask, mask, cv::MORPH_CLOSE, kernel);
    cv::morphologyEx(mask, mask, cv::MORPH_OPEN, kernel);
    
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    
    return contours;
}

std::vector<std::pair<int, cv::Mat>> VisionController::max_contour(
    const std::vector<std::vector<cv::Point>>& contours, 
    const ROI& roi) {
    
    double max_area = 0;
    int max_x = 0, max_y = 0;
    cv::Mat max_cnt;
    
    for (const auto& c : contours) {
        double area = cv::contourArea(c);
        
        if (area > 100 && area > max_area) {
            max_area = area;
            
            // ✅ Usar momentos en lugar de boundingRect (más eficiente)
            cv::Moments m = cv::moments(c);
            if (m.m00 != 0) {
                max_x = static_cast<int>(m.m10 / m.m00) + roi.x1;
                max_y = static_cast<int>(m.m01 / m.m00) + roi.y1;
            }
            
            max_cnt = cv::Mat(c);
        }
    }
    
    std::vector<std::pair<int, cv::Mat>> result;
    result.push_back(std::make_pair(static_cast<int>(max_area), max_cnt));
    result.push_back(std::make_pair(max_x, max_cnt));
    result.push_back(std::make_pair(max_y, max_cnt));
    return result;
}

// ============================================
// MONITORING
// ============================================

size_t VisionController::get_memory_usage_kb() const {
    std::ifstream status("/proc/self/status");
    std::string line;
    
    while (std::getline(status, line)) {
        if (line.find("VmRSS:") == 0) {
            size_t kb = 0;
            sscanf(line.c_str(), "VmRSS: %zu kB", &kb);
            return kb;
        }
    }
    return 0;
}
