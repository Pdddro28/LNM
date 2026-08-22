#include "MeMegaPi.h"
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "Ultrasonic.h"
#include "Adafruit_VL53L0X.h"

// --- Constantes del Sistema ---
#define SERVO_CENTER    90
#define LEFT            0
#define RIGHT           180
#define SERIAL_BAUD     115200
#define SENSOR_TIMEOUT  25000

// Pines de Hardware Fijos
#define BUTTON           A9
#define pinServo         A7
#define trig_front       A15
#define echo_front       A14
#define trig_left        29
#define echo_left        39
#define trig_right       A11
#define echo_right       A10
#define centro           90

// --- Configuración Láser VL53L0X ---
const int XSHUT_PIN1 = 4;
const int XSHUT_PIN2 = 5;

const int LOX1_ADDRESS = 0x30; // Sensor ToF 1
const int LOX2_ADDRESS = 0x29; // Sensor ToF 2

// Instancias de Sensores
Ultrasonic sensorF(trig_front, echo_front);
Ultrasonic sensorL(trig_left, echo_left);
Ultrasonic sensorD(trig_right, echo_right);

Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();

class Carro {
  private:
    MeMegaPiDCMotor motorTraccion;
    Servo servoDireccion;
    Adafruit_MPU6050 mpu;
    
  public:
    // Motor conectado al Puerto 4B de la MegaPi
    Carro() : motorTraccion(PORT4B) {}

    void inicializar() {
      // Configuración del botón (Pull-up interna)
      pinMode(BUTTON, INPUT_PULLUP);

      // Configuración del Servo
      servoDireccion.attach(pinServo);
      servoDireccion.write(centro);
      
      // --- PASO 1: Apagar ambos sensores VL53L0X ---
      pinMode(XSHUT_PIN1, OUTPUT);
      pinMode(XSHUT_PIN2, OUTPUT);
      digitalWrite(XSHUT_PIN1, LOW);
      digitalWrite(XSHUT_PIN2, LOW);
      delay(100); 

      // --- PASO 2: Encender e iniciar SENSOR ToF 1 ---
      pinMode(XSHUT_PIN1, INPUT); // Pone en modo flotante para encender
      delay(100); 
      if (!lox1.begin(LOX1_ADDRESS)) {
        Serial.println("System: VL53L0X - Sensor 1 ERROR");
        while (1);
      }
      delay(10);

      // --- PASO 3: Encender e iniciar SENSOR ToF 2 ---
      pinMode(XSHUT_PIN2, INPUT); 
      delay(100);  
      if (!lox2.begin(LOX2_ADDRESS)) {
        Serial.println("System: VL53L0X - Sensor 2 ERROR");
        while (1);
      }

      Serial.println("System: Hardware and VL53L0X Initialized");
    }

    // --- Lógica de Sensores ---
    bool botonPresionado() {
      return digitalRead(BUTTON) == LOW; 
    }

    long getDistanciaFront() { return sensorF.read(); }
    long getDistanciaLeft()  { return sensorL.read(); }
    long getDistanciaRight() { return sensorD.read(); }

    // Retorna la distancia en CM del VL53L0X número 1
    int getDistanciaLaser1() {
      VL53L0X_RangingMeasurementData_t measure;
      lox1.rangingTest(&measure, false);
      if (measure.RangeStatus != 4) {
        return measure.RangeMilliMeter / 10; // Conversión mm -> cm
      }
      return 255; // Fuera de rango o lectura inválida
    }

    // Retorna la distancia en CM del VL53L0X número 2
    int getDistanciaLaser2() {
      VL53L0X_RangingMeasurementData_t measure;
      lox2.rangingTest(&measure, false);
      if (measure.RangeStatus != 4) {
        return measure.RangeMilliMeter / 10; // Conversión mm -> cm
      }
      return 255; 
    }

    // --- Lógica de Movimiento ---
    void avanzar(byte velocidad) {
      motorTraccion.run(velocidad);
    }

    void retroceder(byte angulo, byte velocidad) {
      servoDireccion.write(centro);
      servoDireccion.write(angulo);
      motorTraccion.run(-velocidad);
    }

    void girarIzquierda(byte angulo, byte velocidad) {
      servoDireccion.write(angulo);
      motorTraccion.run(velocidad);
    }

    void girarDerecha(byte angulo, byte velocidad) {
      servoDireccion.write(angulo);
      motorTraccion.run(velocidad);
    }

    void detenerse() {
      motorTraccion.stop();
      servoDireccion.write(centro);
    }

    void girarCentro() {
      servoDireccion.write(centro);
    }
};

Carro miCarro;
unsigned long timerSensores = 0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  miCarro.inicializar();
}

void loop() {
  // --- PARTE 1: Procesamiento de Comandos (Raspberry -> Arduino) ---
  if (Serial.available() >= 5) {
    byte header = Serial.read();
    if (header == 0xFF) {
      byte tipo   = Serial.read();
      byte accion = Serial.read();
      byte v1     = Serial.read(); 
      byte v2     = Serial.read(); 

      switch (accion) {
        case 1: miCarro.avanzar(v1); break;
        case 2: miCarro.retroceder(v1, v2); break;
        case 3: miCarro.girarIzquierda(v1, v2); break;
        case 4: miCarro.girarDerecha(v1, v2); break;
        case 5: miCarro.detenerse(); break;
        case 6: miCarro.girarCentro(); break;
        case 7: miCarro.inicializar(); break; 
        default: miCarro.detenerse(); break;
      }
    }
  }

  // --- PARTE 2: Telemetría (Arduino -> Raspberry) cada 100ms ---
  if (millis() - timerSensores > 100) {
    int d_front  = (int)miCarro.getDistanciaFront();
    int d_left   = (int)miCarro.getDistanciaLeft();
    
    // NOTA: Como agregaste dos sensores láser, ajusté estas variables para enviarlos.
    int d_laser1 = miCarro.getDistanciaLaser1(); // Sensor ToF Dirección 0x30
    int d_laser2 = miCarro.getDistanciaLaser2(); // Sensor ToF Dirección 0x29
    
    byte estadoBoton = miCarro.botonPresionado() ? 1 : 0;
    
    // ESTRUCTURA DEL PAQUETE MANTENIENDO LOS 8 BYTES
    Serial.write(0xAA);                        // Byte 0: Header de inicio
    Serial.write(constrain(d_front, 0, 255));  // Byte 1: Distancia Frontal (Ultrasónico)
    Serial.write(constrain(d_left, 0, 255));   // Byte 2: Distancia Izquierda (Ultrasónico)
    Serial.write(constrain(d_laser1, 0, 255)); // Byte 3: Reemplaza d_right -> AHORA ES LÁSER ToF 1
    Serial.write(constrain(d_laser2, 0, 255)); // Byte 4: Reemplaza d_rightf -> AHORA ES LÁSER ToF 2
    Serial.write(estadoBoton);                 // Byte 5: Estado del Botón (0 o 1)
    Serial.write(0x00);                        // Byte 6: Relleno (Padding)
    Serial.write(0x00);                        // Byte 7: Relleno (Padding)
    
    timerSensores = millis();
  }
}
