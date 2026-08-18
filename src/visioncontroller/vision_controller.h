#ifndef VISION_CONTROLLER_H
#define VISION_CONTROLLER_H

#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>
#include <vector>
#include <cstdint>
#include <thread> 



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
    
    // Helper methods
    // TODO: Add any private helper methods here

public:
    // --- INITIALIZATION AND CAMERA SETUP ---
    VisionController();
    ~VisionController();
    
    // --- IMAGE ACQUISITION AND PROCESSING ---
    void receive_image();
    
    // --- ANTI-STUCK DETECTION ALGORITHM ---
    bool check_if_stuck();
    void reset_stuck_timer();
    
    // --- DRAWING UTILITIES ---
    void draw_roi(const ROI& roi, const cv::Scalar& color = cv::Scalar(0, 255, 0));
    void draw_contours(const std::vector<std::vector<cv::Point>>& cnt, const ROI& roi, const cv::Scalar& color);
    
    // --- COMPUTER VISION ALGORITHMS ---
    std::vector<std::vector<cv::Point>> find_contours(const std::vector<std::vector<int>>& range_colors, const ROI& roi);
    std::vector<std::pair<int, cv::Mat>> max_contour(const std::vector<std::vector<cv::Point>>& contours, const ROI& roi);
    
    // Getters
    cv::Mat get_frame() const { return frame; }
    int get_width() const { return image_width; }
    int get_height() const { return image_height; }
};

#endif // VISION_CONTROLLER_H
