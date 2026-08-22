#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdio>
#include <memory>
#include <array>
#include <cstdlib>
#include <opencv2/opencv.hpp>

// ==========================================
// VARIABLES GLOBALES
// ==========================================
int L_low = 40, A_low = 130, B_low = 130;
int L_high = 90, A_high = 150, B_high = 150;

std::string status_message = "Listo";
cv::Scalar status_color(0, 255, 0);

void onTrackbar(int, void*) {}

// Offset horizontal donde empieza el panel de controles
const int PANEL_X = 1280;

// ==========================================
// FUNCIONES DE UTILIDAD
// ==========================================
cv::Rect createROI(int x, int y, int width, int height) {
    return cv::Rect(x, y, width, height);
}

void drawROI(cv::Mat& frame, const cv::Rect& roi, 
             const cv::Scalar& color = cv::Scalar(0, 255, 0), int thickness = 2) {
    cv::rectangle(frame, roi, color, thickness);
}

// Deleter personalizado para evitar el warning de atributos en pclose
struct FileDeleter {
    void operator()(FILE* ptr) const {
        if (ptr) pclose(ptr);
    }
};

// Ejecuta comandos de sistema (zenity)
std::string exec_command(const char* cmd) {
    std::array<char, 512> buffer;
    std::string result;
    
    std::unique_ptr<FILE, FileDeleter> pipe(popen(cmd, "r"));
    if (!pipe) return "";
    
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    
    if (!result.empty() && result.back() == '\n') {
        result.pop_back();
    }
    if (result.find("file://") == 0) {
        result = result.substr(7);
    }
    return result;
}

// Obtener la ruta base de la carpeta Colors dinámicamente
std::string getColorsFolderPath() {
    const char* home = getenv("HOME");
    if (home) {
        return std::string(home) + "/Escritorio/LNM/src/Colors/";
    }
    return "./";
}

// ==========================================
// FUNCIONES JSON
// ==========================================
void saveConfigToJSON(const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        status_message = "Error: No se pudo crear el archivo";
        status_color = cv::Scalar(0, 0, 255);
        return;
    }
    
    file << "{\n"
         << "  \"color_bounds\": {\n"
         << "    \"lower\": [" << L_low << ", " << A_low << ", " << B_low << "],\n"
         << "    \"upper\": [" << L_high << ", " << A_high << ", " << B_high << "]\n"
         << "  },\n"
         << "  \"roi\": { \"x\": 100, \"y\": 50, \"width\": 440, \"height\": 270 }\n"
         << "}\n";
    
    file.close();
    status_message = "Guardado exitoso";
    status_color = cv::Scalar(0, 255, 0);
    std::cout << "✓ Configuración guardada en: " << filename << std::endl;
}

void loadConfigFromJSON(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        status_message = "Error: Archivo no encontrado";
        status_color = cv::Scalar(0, 0, 255);
        return;
    }
    
    std::string content((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());
    file.close();
    
    auto extractArray = [](const std::string& text, const std::string& key, int& v1, int& v2, int& v3) -> bool {
        size_t pos = text.find("\"" + key + "\"");
        if (pos == std::string::npos) return false;
        
        pos = text.find("[", pos);
        if (pos == std::string::npos) return false;
        
        size_t end = text.find("]", pos);
        if (end == std::string::npos) return false;
        
        std::string arrayStr = text.substr(pos + 1, end - pos - 1);
        
        std::vector<int> values;
        std::string token;
        for (char c : arrayStr) {
            if (c == ',' || c == ' ' || c == '\t' || c == '\n' || c == '\r') {
                if (!token.empty()) {
                    try {
                        values.push_back(std::stoi(token));
                    } catch (...) {}
                    token.clear();
                }
            } else if (isdigit(c) || c == '-') {
                token += c;
            }
        }
        if (!token.empty()) {
            try {
                values.push_back(std::stoi(token));
            } catch (...) {}
        }
        
        if (values.size() >= 3) {
            v1 = values[0];
            v2 = values[1];
            v3 = values[2];
            return true;
        }
        return false;
    };
    
    bool success = true;
    success &= extractArray(content, "lower", L_low, A_low, B_low);
    success &= extractArray(content, "upper", L_high, A_high, B_high);
    
    if (!success) {
        status_message = "Error: Formato JSON inválido";
        status_color = cv::Scalar(0, 0, 255);
        std::cout << "✗ Error al parsear el archivo JSON" << std::endl;
        return;
    }
    
    cv::setTrackbarPos("L_low", "Vision", L_low);
    cv::setTrackbarPos("A_low", "Vision", A_low);
    cv::setTrackbarPos("B_low", "Vision", B_low);
    cv::setTrackbarPos("L_high", "Vision", L_high);
    cv::setTrackbarPos("A_high", "Vision", A_high);
    cv::setTrackbarPos("B_high", "Vision", B_high);
    
    status_message = "Cargado exitosamente";
    status_color = cv::Scalar(0, 255, 0);
    std::cout << "✓ Configuración cargada desde: " << filename << std::endl;
    std::cout << "  Lower: [" << L_low << ", " << A_low << ", " << B_low << "]" << std::endl;
    std::cout << "  Upper: [" << L_high << ", " << A_high << ", " << B_high << "]" << std::endl;
}

// ==========================================
// DETECCIÓN DE CLICS EN BOTONES
// ==========================================
void onMouse(int event, int x, int y, int flags, void* userdata) {
    if (event == cv::EVENT_LBUTTONDOWN) {
        // Los botones ahora están en el panel derecho (offset PANEL_X)
        cv::Rect btn_save(PANEL_X + 20, 10, 260, 40);
        cv::Rect btn_load(PANEL_X + 20, 60, 260, 40);
        
        if (btn_save.contains(cv::Point(x, y))) {
            std::cout << "Abriendo diálogo de guardado en carpeta Colors..." << std::endl;
            std::string default_path = getColorsFolderPath() + "mask_nuevo.json";
            std::string cmd = "zenity --file-selection --save --confirm-overwrite --title=\"Guardar configuración JSON\" --filename=\"" + default_path + "\"";
            
            std::string filepath = exec_command(cmd.c_str());
            if (!filepath.empty()) {
                saveConfigToJSON(filepath);
            } else {
                status_message = "Guardado cancelado";
                status_color = cv::Scalar(0, 100, 255);
            }
        } 
        else if (btn_load.contains(cv::Point(x, y))) {
            std::cout << "Abriendo diálogo de carga en carpeta Colors..." << std::endl;
            std::string default_dir = getColorsFolderPath();
            std::string cmd = "zenity --file-selection --title=\"Cargar configuración JSON\" --filename=\"" + default_dir + "\"";
            
            std::string filepath = exec_command(cmd.c_str());
            if (!filepath.empty()) {
                loadConfigFromJSON(filepath);
            } else {
                status_message = "Carga cancelada";
                status_color = cv::Scalar(0, 100, 255);
            }
        }
    }
}

// ==========================================
// FUNCIÓN PRINCIPAL
// ==========================================
int main() {
    std::cout << "=== SISTEMA DE VISIÓN TODO EN UNA VENTANA ===" << std::endl;
    std::cout << "Carpeta de trabajo: " << getColorsFolderPath() << std::endl;
    
    cv::VideoCapture cap(0, cv::CAP_V4L2);
    if (!cap.isOpened()) {
        std::cerr << "Error: No se pudo abrir la cámara" << std::endl;
        return -1;
    }
    
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 370);
    
    cv::Rect my_roi = createROI(100, 50, 440, 270);
    cv::Mat frame, lab_frame, mask;
    
    // ==========================================
    // UNA SOLA VENTANA
    // ==========================================
    std::string win_vision = "Vision";
    cv::namedWindow(win_vision, cv::WINDOW_AUTOSIZE);
    cv::moveWindow(win_vision, 0, 0);
    
    // Trackbars en la ventana principal
    cv::createTrackbar("L_low", win_vision, &L_low, 255, onTrackbar);
    cv::createTrackbar("A_low", win_vision, &A_low, 255, onTrackbar);
    cv::createTrackbar("B_low", win_vision, &B_low, 255, onTrackbar);
    cv::createTrackbar("L_high", win_vision, &L_high, 255, onTrackbar);
    cv::createTrackbar("A_high", win_vision, &A_high, 255, onTrackbar);
    cv::createTrackbar("B_high", win_vision, &B_high, 255, onTrackbar);
    
    cv::setMouseCallback(win_vision, onMouse, nullptr);
    
    std::cout << "Haz clic en los botones del panel derecho." << std::endl;
    std::cout << "El explorador se abrirá directamente en: ~/Escritorio/LNM/src/Colors/" << std::endl;
    std::cout << "Presiona 'q' o ESC para salir." << std::endl;
    
    while (true) {
        cap.read(frame);
        if (frame.empty()) break;
        
        cv::flip(frame, frame, 1);
        cv::cvtColor(frame, lab_frame, cv::COLOR_BGR2Lab);
        
        std::vector<cv::Mat> channels;
        cv::split(lab_frame, channels);
        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(3.0, cv::Size(8, 8));
        clahe->apply(channels[0], channels[0]);
        cv::merge(channels, lab_frame);
        cv::GaussianBlur(lab_frame, lab_frame, cv::Size(7, 7), 0);
        
        cv::Mat roi_img = lab_frame(my_roi);
        mask = cv::Mat::zeros(frame.size(), CV_8UC1);
        cv::Mat roi_mask = mask(my_roi);
        
        cv::Scalar lower_bound(L_low, A_low, B_low);
        cv::Scalar upper_bound(L_high, A_high, B_high);
        
        cv::inRange(roi_img, lower_bound, upper_bound, roi_mask);
        
        cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(5, 5));
        cv::morphologyEx(roi_mask, roi_mask, cv::MORPH_CLOSE, kernel);
        cv::morphologyEx(roi_mask, roi_mask, cv::MORPH_OPEN, kernel);
        
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
        
        double max_area = 0;
        std::vector<cv::Point> max_contour;
        int max_idx = -1;
        
        for (size_t i = 0; i < contours.size(); i++) {
            if (contours[i].empty()) continue;
            double area = cv::contourArea(contours[i]);
            if (area > max_area) {
                max_area = area;
                max_contour = contours[i];
                max_idx = static_cast<int>(i);
            }
        }
        
        cv::Mat display_frame = frame.clone();
        if (max_area > 0 && !max_contour.empty() && max_idx >= 0) {
            cv::drawContours(display_frame, contours, max_idx, cv::Scalar(0, 255, 0), 3);
            cv::Moments M = cv::moments(max_contour);
            if (M.m00 != 0) {
                int cx = static_cast<int>(M.m10 / M.m00);
                int cy = static_cast<int>(M.m01 / M.m00);
                cv::circle(display_frame, cv::Point(cx, cy), 8, cv::Scalar(255, 0, 0), -1);
                cv::putText(display_frame, "Centro: (" + std::to_string(cx) + ", " + std::to_string(cy) + ")", 
                            cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 0, 0), 2);
            }
            cv::putText(display_frame, "Area: " + std::to_string((int)max_area) + " px", 
                        cv::Point(10, 60), cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 255, 0), 2);
        } else {
            cv::putText(display_frame, "No se detecto objeto", cv::Point(10, 30),
                        cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 0, 255), 2);
        }
        drawROI(display_frame, my_roi);
        
        // ==========================================
        // CANVAS UNIFICADO: Vision (1280) + Controles (300)
        // ==========================================
        int panel_width = 300;
        int canvas_width = PANEL_X + panel_width;  // 1580
        int canvas_height = frame.rows;            // 370
        cv::Mat canvas(canvas_height, canvas_width, CV_8UC3, cv::Scalar(0, 0, 0));
        
        // Copiar frame original a la izquierda
        cv::Mat left_half = canvas(cv::Rect(0, 0, frame.cols, frame.rows));
        display_frame.copyTo(left_half);
        
        // Copiar máscara a la derecha
        cv::Mat mask_display;
        cv::cvtColor(mask, mask_display, cv::COLOR_GRAY2BGR);
        cv::putText(mask_display, "MASCARA DE SEGMENTACION", cv::Point(10, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 255, 255), 2);
        
        cv::Mat right_half = canvas(cv::Rect(frame.cols, 0, frame.cols, frame.rows));
        mask_display.copyTo(right_half);
        
        // Etiquetas en la parte inferior de cada lado
        cv::putText(canvas, "FRAME ORIGINAL", cv::Point(10, canvas_height - 15),
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 0), 2);
        cv::putText(canvas, "MASCARA", cv::Point(frame.cols + 10, canvas_height - 15),
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 0), 2);
        
        // Líneas divisorias
        cv::line(canvas, cv::Point(frame.cols, 0), cv::Point(frame.cols, canvas_height), 
                 cv::Scalar(255, 255, 255), 2);
        cv::line(canvas, cv::Point(PANEL_X, 0), cv::Point(PANEL_X, canvas_height), 
                 cv::Scalar(255, 255, 255), 2);
        
        // ==========================================
        // PANEL DE CONTROLES (lado derecho)
        // ==========================================
        cv::Mat panel = canvas(cv::Rect(PANEL_X, 0, panel_width, canvas_height));
        panel.setTo(cv::Scalar(240, 240, 240));  // Fondo gris claro
        
        // Botón GUARDAR
        cv::Rect btn_save(20, 10, 260, 40);
        cv::rectangle(panel, btn_save, cv::Scalar(0, 150, 0), cv::FILLED);
        cv::rectangle(panel, btn_save, cv::Scalar(0, 100, 0), 2);
        cv::putText(panel, "GUARDAR JSON", cv::Point(btn_save.x + 65, btn_save.y + 26), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2);
        
        // Botón CARGAR
        cv::Rect btn_load(20, 60, 260, 40);
        cv::rectangle(panel, btn_load, cv::Scalar(0, 100, 200), cv::FILLED);
        cv::rectangle(panel, btn_load, cv::Scalar(0, 50, 150), 2);
        cv::putText(panel, "CARGAR JSON", cv::Point(btn_load.x + 65, btn_load.y + 26), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2);
        
        // Estado
        cv::putText(panel, "ESTADO:", cv::Point(10, 130), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 0), 1);
        cv::putText(panel, status_message, cv::Point(10, 160), cv::FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1);
        
        // Valores actuales
        std::string vals = "L[" + std::to_string(L_low) + "-" + std::to_string(L_high) + "] "
                          "A[" + std::to_string(A_low) + "-" + std::to_string(A_high) + "] "
                          "B[" + std::to_string(B_low) + "-" + std::to_string(B_high) + "]";
        cv::putText(panel, vals, cv::Point(10, 210), cv::FONT_HERSHEY_SIMPLEX, 0.4, cv::Scalar(100, 100, 100), 1);
        
        // ==========================================
        // MOSTRAR LA ÚNICA VENTANA
        // ==========================================
        cv::imshow(win_vision, canvas);
        
        char key = (char)cv::waitKey(1);
        if (key == 'q' || key == 27) break;
    }
    
    cap.release();
    cv::destroyAllWindows();
    std::cout << "Programa finalizado." << std::endl;
    return 0;
}