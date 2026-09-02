#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdio>
#include <memory>
#include <array>
#include <cstdlib>
#include <algorithm>
#include <opencv2/opencv.hpp>

// ==========================================
// ESTRUCTURAS DE DATOS
// ==========================================
struct ROI {
    int x1, y1, x2, y2;
};

// ==========================================
// VARIABLES GLOBALES
// ==========================================
bool drawing = false;
int ix = -1, iy = -1;
std::vector<ROI> rois;
ROI temp_rect = {-1, -1, -1, -1};

int window_width = 640;
int window_height = 370;

// Variables para el mapeo de coordenadas (letterboxing)
double scale_factor = 1.0;
int offset_x = 0;
int offset_y = 0;
int frame_width = 640;
int frame_height = 370;

// ==========================================
// FUNCIONES DE UTILIDAD DEL SISTEMA
// ==========================================
struct FileDeleter {
    void operator()(FILE* ptr) const {
        if (ptr) pclose(ptr);
    }
};

std::string exec_command(const char* cmd) {
    std::array<char, 512> buffer;
    std::string result;
    std::unique_ptr<FILE, FileDeleter> pipe(popen(cmd, "r"));
    if (!pipe) return "";
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    if (!result.empty() && result.back() == '\n') result.pop_back();
    if (result.find("file://") == 0) result = result.substr(7);
    return result;
}

// Carpeta específica para los archivos JSON de ROIs
std::string getROIFolderPath() {
    const char* home = getenv("HOME");
    if (home) {
        return std::string(home) + "/Escritorio/LNM/src/ROI/";
    }
    return "./";
}

// ==========================================
// FUNCIONES DE IMPORTAR / EXPORTAR
// ==========================================
void export_rois_dialog() {
    if (rois.empty()) {
        std::cout << "⚠ No hay ROIs para exportar" << std::endl;
        return;
    }
    
    std::string default_path = getROIFolderPath() + "rois.json";
    std::string cmd = "zenity --file-selection --save --confirm-overwrite --title=\"Exportar ROIs a JSON\" --filename=\"" + default_path + "\"";
    std::string filepath = exec_command(cmd.c_str());
    
    if (filepath.empty()) {
        std::cout << "Exportación cancelada" << std::endl;
        return;
    }

    std::ofstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Error: No se pudo crear el archivo" << std::endl;
        return;
    }

    file << "{\n  \"rois\": [\n";
    for (size_t i = 0; i < rois.size(); ++i) {
        file << "    {\"x1\": " << rois[i].x1 << ", \"y1\": " << rois[i].y1 
             << ", \"x2\": " << rois[i].x2 << ", \"y2\": " << rois[i].y2 << "}";
        if (i < rois.size() - 1) file << ",";
        file << "\n";
    }
    file << "  ]\n}\n";
    
    file.close();
    std::cout << "✓ ROIs exportados exitosamente a: " << filepath << std::endl;
}

void import_rois_dialog() {
    std::string default_dir = getROIFolderPath();
    std::string cmd = "zenity --file-selection --title=\"Importar ROIs desde JSON\" --filename=\"" + default_dir + "\"";
    std::string filepath = exec_command(cmd.c_str());
    
    if (filepath.empty()) {
        std::cout << "Importación cancelada" << std::endl;
        return;
    }

    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Error: No se pudo abrir el archivo" << std::endl;
        return;
    }

    std::string content((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    rois.clear();
    size_t pos = 0;
    
    // Parseo simple y robusto del JSON
    while ((pos = content.find("{", pos)) != std::string::npos) {
        size_t end = content.find("}", pos);
        if (end == std::string::npos) break;
        
        std::string obj = content.substr(pos, end - pos + 1);
        
        auto extractInt = [&](const std::string& key) -> int {
            size_t kpos = obj.find("\"" + key + "\"");
            if (kpos == std::string::npos) return -1;
            size_t cpos = obj.find(":", kpos);
            if (cpos == std::string::npos) return -1;
            size_t npos = obj.find_first_of("0123456789-", cpos);
            if (npos == std::string::npos) return -1;
            return std::stoi(obj.substr(npos));
        };

        int x1 = extractInt("x1");
        int y1 = extractInt("y1");
        int x2 = extractInt("x2");
        int y2 = extractInt("y2");

        if (x1 != -1 && y1 != -1 && x2 != -1 && y2 != -1) {
            int rx1 = std::min(x1, x2);
            int ry1 = std::min(y1, y2);
            int rx2 = std::max(x1, x2);
            int ry2 = std::max(y1, y2);
            rois.push_back({rx1, ry1, rx2, ry2});
        }
        
        pos = end + 1;
    }
    
    std::cout << "✓ ROIs importados: " << rois.size() << " encontrados en " << filepath << std::endl;
}

// ==========================================
// CALLBACK DEL MOUSE
// ==========================================
void mouse_callback(int event, int x, int y, int flags, void* userdata) {
    // Zona de botones (parte superior, y < 50)
    if (y < 50) {
        if (event == cv::EVENT_LBUTTONDOWN) {
            cv::Rect btn_import(10, 5, 130, 40);
            cv::Rect btn_export(150, 5, 130, 40);
            cv::Rect btn_clear(290, 5, 130, 40);
            
            if (btn_import.contains(cv::Point(x, y))) {
                import_rois_dialog();
            } else if (btn_export.contains(cv::Point(x, y))) {
                export_rois_dialog();
            } else if (btn_clear.contains(cv::Point(x, y))) {
                rois.clear();
                std::cout << "✓ Todos los ROIs han sido limpiados" << std::endl;
            }
        }
        return; // No permitir dibujar en la zona de botones
    }

    // 1. Mapear coordenadas de la ventana al frame original
    int orig_x = static_cast<int>((x - offset_x) / scale_factor);
    int orig_y = static_cast<int>((y - offset_y) / scale_factor);

    // 2. Limitar para que no se salga del frame original
    orig_x = std::max(0, std::min(orig_x, frame_width));
    orig_y = std::max(0, std::min(orig_y, frame_height));

    if (event == cv::EVENT_LBUTTONDOWN) {
        drawing = true;
        ix = orig_x;
        iy = orig_y;
    } 
    else if (event == cv::EVENT_MOUSEMOVE) {
        if (drawing) {
            temp_rect = {ix, iy, orig_x, orig_y};
        }
    } 
    else if (event == cv::EVENT_LBUTTONUP) {
        drawing = false;
        
        // Asegurar que x1 < x2 y y1 < y2
        int rx1 = std::min(ix, orig_x);
        int ry1 = std::min(iy, orig_y);
        int rx2 = std::max(ix, orig_x);
        int ry2 = std::max(iy, orig_y);

        // Evitar guardar clics accidentales muy pequeños
        if (rx2 - rx1 > 5 && ry2 - ry1 > 5) {
            rois.push_back({rx1, ry1, rx2, ry2});
            std::cout << "✓ ROI agregado: [" << rx1 << ", " << ry1 << "] a [" << rx2 << ", " << ry2 << "]" << std::endl;
        }
        
        temp_rect = {-1, -1, -1, -1};
    }
}

// ==========================================
// FUNCIÓN PRINCIPAL
// ==========================================
int main() {
    std::cout << "=== DETECTOR DE ROIs ===" << std::endl;
    std::cout << "Instrucciones:" << std::endl;
    std::cout << " - AGREGAR: Haz clic y arrastra el mouse sobre el video" << std::endl;
    std::cout << " - IMPORTAR: Carga un archivo JSON existente" << std::endl;
    std::cout << " - EXPORTAR: Guarda los ROIs actuales en un JSON" << std::endl;
    std::cout << " - LIMPIAR: Borra todos los ROIs de la pantalla" << std::endl;
    std::cout << " - Presiona 'q' o 'ESC' para salir" << std::endl;

    cv::VideoCapture cap(0, cv::CAP_V4L2);
    if (!cap.isOpened()) {
        std::cerr << "Error: No se pudo acceder a la cámara" << std::endl;
        return -1;
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 370);

    std::string window_name = "ROI Detector";
    cv::namedWindow(window_name, cv::WINDOW_NORMAL);
    cv::resizeWindow(window_name, window_width, window_height);

    cv::setMouseCallback(window_name, mouse_callback, nullptr);

    while (true) {
        cv::Mat frame;
        cap >> frame;
        if (frame.empty()) break;
        cv::flip(frame, frame, 1);

        // Actualizar dimensiones reales del frame
        frame_height = frame.rows;
        frame_width = frame.cols;

        // 1. Calcular escala para ajustar manteniendo proporción (dejando margen para botones)
        double scale_w = (double)(window_width - 40) / frame_width;
        double scale_h = (double)(window_height - 100) / frame_height; // 50px arriba botones, 50px abajo margen
        scale_factor = std::min(scale_w, scale_h);

        int new_w = static_cast<int>(frame_width * scale_factor);
        int new_h = static_cast<int>(frame_height * scale_factor);

        // 2. Redimensionar frame
        cv::Mat resized;
        cv::resize(frame, resized, cv::Size(new_w, new_h));

        // 3. Calcular posición centrada (con margen superior de 50px para los botones)
        int top = 60 + (window_height - 100 - new_h) / 2;
        int left = 20 + (window_width - 40 - new_w) / 2;

        offset_x = left;
        offset_y = top;

        // 4. Crear canvas con fondo oscuro elegante
        cv::Mat display(window_height, window_width, CV_8UC3, cv::Scalar(30, 30, 30));

        // ==========================================
        // DIBUJAR BOTONES DE INTERFAZ
        // ==========================================
        cv::Rect btn_import(10, 5, 130, 40);
        cv::rectangle(display, btn_import, cv::Scalar(0, 100, 200), cv::FILLED);
        cv::rectangle(display, btn_import, cv::Scalar(0, 150, 255), 2);
        cv::putText(display, "IMPORTAR", cv::Point(btn_import.x + 20, btn_import.y + 26), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2);

        cv::Rect btn_export(150, 5, 130, 40);
        cv::rectangle(display, btn_export, cv::Scalar(0, 150, 0), cv::FILLED);
        cv::rectangle(display, btn_export, cv::Scalar(0, 200, 0), 2);
        cv::putText(display, "EXPORTAR", cv::Point(btn_export.x + 20, btn_export.y + 26), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2);

        cv::Rect btn_clear(290, 5, 130, 40);
        cv::rectangle(display, btn_clear, cv::Scalar(150, 0, 0), cv::FILLED);
        cv::rectangle(display, btn_clear, cv::Scalar(200, 0, 0), 2);
        cv::putText(display, "LIMPIAR", cv::Point(btn_clear.x + 25, btn_clear.y + 26), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 255, 255), 2);
                    
        cv::putText(display, "Dibuja con el mouse para AGREGAR un ROI", cv::Point(440, 30), 
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(200, 200, 200), 1);

        // Copiar el frame redimensionado en el canvas
        cv::Rect roi_frame(left, top, new_w, new_h);
        cv::Mat frame_roi = display(roi_frame);
        resized.copyTo(frame_roi);

        // 5. Dibujar ROIs guardados
        for (size_t i = 0; i < rois.size(); ++i) {
            int dx1 = static_cast<int>(rois[i].x1 * scale_factor) + offset_x;
            int dy1 = static_cast<int>(rois[i].y1 * scale_factor) + offset_y;
            int dx2 = static_cast<int>(rois[i].x2 * scale_factor) + offset_x;
            int dy2 = static_cast<int>(rois[i].y2 * scale_factor) + offset_y;

            cv::rectangle(display, cv::Point(dx1, dy1), cv::Point(dx2, dy2), cv::Scalar(0, 255, 0), 2);

            int width = rois[i].x2 - rois[i].x1;
            int height = rois[i].y2 - rois[i].y1;
            std::string label = "ROI " + std::to_string(i + 1) + ": " + std::to_string(width) + "x" + std::to_string(height);
            
            int text_y = std::max(top + 15, dy1 - 5);
            cv::putText(display, label, cv::Point(dx1, text_y), cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0, 255, 0), 1);
        }

        // 6. Dibujar ROI temporal (el que se está arrastrando)
        if (temp_rect.x1 != -1) {
            int dx1 = static_cast<int>(std::min(temp_rect.x1, temp_rect.x2) * scale_factor) + offset_x;
            int dy1 = static_cast<int>(std::min(temp_rect.y1, temp_rect.y2) * scale_factor) + offset_y;
            int dx2 = static_cast<int>(std::max(temp_rect.x1, temp_rect.x2) * scale_factor) + offset_x;
            int dy2 = static_cast<int>(std::max(temp_rect.y1, temp_rect.y2) * scale_factor) + offset_y;

            cv::rectangle(display, cv::Point(dx1, dy1), cv::Point(dx2, dy2), cv::Scalar(0, 255, 255), 2);
        }

        cv::imshow(window_name, display);

        char key = (char)cv::waitKey(1);
        if (key == 'q' || key == 27) break;
    }

    cap.release();
    cv::destroyAllWindows();
    
    // Preguntar si desea exportar al salir (opcional, pero útil)
    if (!rois.empty()) {
        std::cout << "\n¿Deseas exportar los ROIs antes de salir? (s/n): ";
        char ans;
        std::cin >> ans;
        if (ans == 's' || ans == 'S') {
            export_rois_dialog();
        }
    }

    std::cout << "Programa finalizado." << std::endl;
    return 0;
}
