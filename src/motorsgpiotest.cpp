#include <iostream>
#include <gpiod.hpp>
#include <chrono>
#include <thread>

const gpiod::line::offset SERVO_PIN = 18;
const gpiod::line::offset MOTOR_IN1 = 19;
const gpiod::line::offset MOTOR_IN2 = 13;
const gpiod::line::offset MOTOR_SLEEP = 5;

// PWM por software para servo (50Hz)
void mover_servo(gpiod::line_request& req, int angulo) {
    int pulso_us = 1000 + (angulo * 1000 / 180);
    
    for (int i = 0; i < 50; ++i) {
        req.set_value(SERVO_PIN, gpiod::line::value::ACTIVE);
        std::this_thread::sleep_for(std::chrono::microseconds(pulso_us));
        req.set_value(SERVO_PIN, gpiod::line::value::INACTIVE);
        std::this_thread::sleep_for(std::chrono::microseconds(20000 - pulso_us));
    }
}

// PWM por software para motor (20kHz)
void controlar_motor(gpiod::line_request& req, int velocidad_pct, int direccion, int duracion_ms = 1000) {
    const int periodo_us = 50; // 20kHz
    int pulso_activo_us = (velocidad_pct * periodo_us) / 100;
    int pulso_inactivo_us = periodo_us - pulso_activo_us;
    
    int ciclos = (duracion_ms * 1000) / periodo_us;
    
    for (int i = 0; i < ciclos; ++i) {
        if (direccion == 1) {
            req.set_value(MOTOR_IN1, gpiod::line::value::ACTIVE);
            req.set_value(MOTOR_IN2, gpiod::line::value::INACTIVE);
        } else if (direccion == 2) {
            req.set_value(MOTOR_IN1, gpiod::line::value::INACTIVE);
            req.set_value(MOTOR_IN2, gpiod::line::value::ACTIVE);
        } else {
            req.set_value(MOTOR_IN1, gpiod::line::value::INACTIVE);
            req.set_value(MOTOR_IN2, gpiod::line::value::INACTIVE);
            break;
        }
        
        if (pulso_activo_us > 0) {
            std::this_thread::sleep_for(std::chrono::microseconds(pulso_activo_us));
        }
        if (pulso_inactivo_us > 0) {
            std::this_thread::sleep_for(std::chrono::microseconds(pulso_inactivo_us));
        }
    }
    
    req.set_value(MOTOR_IN1, gpiod::line::value::INACTIVE);
    req.set_value(MOTOR_IN2, gpiod::line::value::INACTIVE);
}


int main() {
    std::cout << "=== PRUEBA SERVO + MOTOR DC (DRV8833) ===" << std::endl;
    
    try {
        auto chip = gpiod::chip("/dev/gpiochip0"); 
        
        // 1. Configurar la petición global (consumer)
        gpiod::request_config req_cfg;
        req_cfg.set_consumer("robot_motors");
        
        // 2. Configurar las propiedades de los pines
        gpiod::line_config line_cfg;
        gpiod::line_settings settings;
        settings.set_direction(gpiod::line::direction::OUTPUT);
        
        line_cfg.add_line_settings({SERVO_PIN, MOTOR_IN1, MOTOR_IN2, MOTOR_SLEEP}, settings);
        
        // 3. CORRECCIÓN V2: Se solicita a través de chip.prepare_request() o instanciando el request
        auto req = chip.prepare_request()
                       .set_request_config(req_cfg)
                       .set_line_config(line_cfg)
                       .do_request();
        
        req.set_value(MOTOR_SLEEP, gpiod::line::value::ACTIVE);
        std::cout << "✓ DRV8833 activado" << std::endl;
        
        std::cout << "\n[1] Servo → 120° (centro)" << std::endl;
        mover_servo(req, 120);
        std::this_thread::sleep_for(std::chrono::seconds(2));
        
        std::cout << "[2] Motor → ADELANTE 50% (2s)" << std::endl;
        controlar_motor(req, 50, 1, 2000);
        
        std::cout << "[3] Servo → 80° (izquierda)" << std::endl;
        mover_servo(req, 80);
        std::this_thread::sleep_for(std::chrono::seconds(2));
        
        std::cout << "[4] Motor → ATRÁS 75% (2s)" << std::endl;
        controlar_motor(req, 75, 2, 2000);
        
        std::cout << "[5] Servo → 150° (derecha)" << std::endl;
        mover_servo(req, 150);
        std::this_thread::sleep_for(std::chrono::seconds(2));
        
        std::cout << "[6] Motor → ADELANTE 90% (1s)" << std::endl;
        controlar_motor(req, 90, 1, 1000);
        
        std::cout << "[7] Parando todo..." << std::endl;
        controlar_motor(req, 0, 0);
        mover_servo(req, 90);
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        std::cout << "\n✅ Prueba completada" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return -1;
    }
    
    return 0;
}
