#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    // Pipeline optimizado con drop=true y sync=false para evitar bloqueos
    std::string pipeline = "libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! "
                           "videoconvert ! video/x-raw, format=BGR ! "
                           "appsink drop=true sync=false";

    std::cout << "Abriendo la c�mara..." << std::endl;
    cv::VideoCapture cap(pipeline, cv::CAP_GSTREAMER);

    if (!cap.isOpened()) {
        std::cerr << "Error: No se pudo abrir la c�mara con GStreamer." << std::endl;
        return -1;
    }

    std::cout << "�C�mara abierta con �xito! Presiona ESC para salir." << std::endl;

    cv::Mat frame;
    while (true) {
        // Usar cap.read(frame) es equivalente a cap >> frame pero permite validar mejor
        if (!cap.read(frame) || frame.empty()) {
            std::cerr << "Advertencia: Frame vac�o o error de lectura." << std::endl;
            continue; // Intentar con el siguiente frame en lugar de romper el bucle
        }

        cv::imshow("Pi Camera - C++ / OpenCV", frame);

        if (cv::waitKey(1) == 27) { // Tecla ESC
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}