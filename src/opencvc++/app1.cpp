#include <iostream>
#include <opencv2/opencv.hpp>

// ==========================================
// FUNCIONES MODULARES DE VISIÓN
// ==========================================

// 1. Crear y definir un ROI (Region of Interest)
cv::Rect createROI(int x, int y, int width, int height) {
    return cv::Rect(x, y, width, height);
}

// 2. Dibujar el ROI en el frame (separar la lógica de dibujo de la de procesamiento)
void drawROI(cv::Mat& frame, const cv::Rect& roi, const cv::Scalar& color = cv::Scalar(0, 255, 0), int thickness = 2) {
    cv::rectangle(frame, roi, color, thickness);
}

// 3. Crear la máscara segmentada y morfologizada
// NOTA: 'src' es const reference (solo lectura, cero copias). 
// 'out_mask' es reference (la función escribirá el resultado aquí).
void createMask(const cv::Mat& src, const cv::Rect& roi, 
                const cv::Scalar& lower_bound, const cv::Scalar& upper_bound, 
                cv::Mat& out_mask) {
    
    // A. Extraer la región de interés (esto crea una "vista", no copia los datos)
    cv::Mat roi_img = src(roi);

    // B. Umbralización de color en el espacio LAB
    cv::inRange(roi_img, lower_bound, upper_bound, out_mask);

    // C. Operaciones morfológicas para limpiar la máscara
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(5, 5));
    cv::morphologyEx(out_mask, out_mask, cv::MORPH_CLOSE, kernel); // Rellenar huecos
    cv::morphologyEx(out_mask, out_mask, cv::MORPH_OPEN, kernel);  // Eliminar ruido
}

// ==========================================
// FUNCIÓN PRINCIPAL
// ==========================================
int main() {
    cv::VideoCapture cap(0, cv::CAP_V4L2);
    if (!cap.isOpened()) {
        std::cerr << "Error: No se pudo abrir la cámara." << std::endl;
        return -1;
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 370);
    cap.set(cv::CAP_PROP_FPS, 32);

    cv::Mat frame;
    cv::Mat lab_frame;
    cv::Mat mask; // Se reutiliza en cada iteración para evitar reservar memoria constantemente

    // Definimos el ROI una sola vez al inicio
    cv::Rect my_roi = createROI(100, 50, 440, 270);

    // Límites de color LAB (¡Ajusta estos valores a tu objeto!)
    cv::Scalar lower_bound(40, 130, 130); 
    cv::Scalar upper_bound(90, 150, 150); 

    std::cout << "Cámara iniciada. Presiona 'q' para salir." << std::endl;

    while (true) {
        cap.read(frame);
        if (frame.empty()) break;

        // Voltear y convertir a LAB
        cv::flip(frame, frame, 1);
        cv::cvtColor(frame, lab_frame, cv::COLOR_BGR2Lab);

        // CLAHE y Blur (Preprocesamiento)
        std::vector<cv::Mat> channels;
        cv::split(lab_frame, channels);
        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(3.0, cv::Size(8, 8));
        clahe->apply(channels[0], channels[0]);
        cv::merge(channels, lab_frame);
        cv::GaussianBlur(lab_frame, lab_frame, cv::Size(7, 7), 0);

        // --- AQUÍ USAMOS NUESTRAS FUNCIONES MODULARES ---
        
        // 1. Generar la máscara
        createMask(lab_frame, my_roi, lower_bound, upper_bound, mask);

        // 2. Dibujar el ROI en el frame original para visualización
        drawROI(frame, my_roi);

        // Visualización
        cv::imshow("Original con ROI", frame);
        cv::imshow("Mascara Segmentada", mask);

        char key = (char)cv::waitKey(1);
        if (key == 'q' || key == 27) {
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    std::cout << "Programa finalizado correctamente." << std::endl;
    return 0;
}