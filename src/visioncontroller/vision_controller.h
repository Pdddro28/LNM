#ifndef VISION_CONTROLLER_H
#define VISION_CONTROLLER_H

#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <cstdint>

// ============================================
// TIPO DE CÁMARA (FLAG PARA CAMBIAR FÁCILMENTE)
// ============================================
enum class CameraBackend {
    V4L2,           // Para cámaras USB o con driver legacy
    GSTREAMER       // Para Raspberry Pi con libcamera (recomendado)
};

// --- DATA STRUCTURES ---
struct ROI {
    int x1, y1;
    int x2, y2;
};

// --- VISION SYSTEM CONTROLLER ---
class VisionController {
private:
    // Camera and frame properties
    int image_width;
    int image_height;
    cv::Mat frame;
    cv::Mat image_lab;
    
    // Camera object
    cv::VideoCapture camera;
    
    CameraBackend backend_type;
    
    std::string gstreamer_pipeline;

public:
    explicit VisionController(CameraBackend backend = CameraBackend::GSTREAMER);
    ~VisionController();
    
    // --- IMAGE ACQUISITION AND PROCESSING ---
    void receive_image();
    
    // --- DRAWING UTILITIES ---
    void draw_roi(const ROI& roi, const cv::Scalar& color = cv::Scalar(0, 255, 0));
    void draw_contours(const std::vector<std::vector<cv::Point>>& cnt, 
                       const ROI& roi, const cv::Scalar& color);
    
    // --- COMPUTER VISION ALGORITHMS ---
    std::vector<std::vector<cv::Point>> find_contours(
        const std::vector<std::vector<int>>& range_colors, const ROI& roi);
    
    std::vector<std::pair<int, cv::Mat>> max_contour(
        const std::vector<std::vector<cv::Point>>& contours, const ROI& roi);
    
    // --- MONITORING ---
    size_t get_memory_usage_kb() const;
    
    // Getters
    cv::Mat get_frame() const { return frame; }
    int get_width() const { return image_width; }
    int get_height() const { return image_height; }
    CameraBackend get_backend() const { return backend_type; }
};

#endif // VISION_CONTROLLER_H