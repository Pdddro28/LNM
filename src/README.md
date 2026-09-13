# Source Code

En esta carpeta se encuentra el código principal de nuestro robot

# Instalación en *shell*

```
#!/bin/bash

# ==========================================
# SCRIPT DE INSTALACIÓN: OpenCV (C++) + GStreamer + GPIO
# Optimizado para Raspberry Pi Zero (Bookworm/Bullseye)
# SIN soporte de Python
# ==========================================

set -e # Detener el script si ocurre un error

echo "=================================================="
echo " 🚀 Iniciando instalación del entorno de Visión y GPIO (C++)"
echo "=================================================="

# 1. Actualizar el sistema
echo "[1/5] Actualizando lista de paquetes del sistema..."
sudo apt update -y
sudo apt upgrade -y

# 2. Instalar dependencias de GStreamer y Cámara (libcamera)
echo "[2/5] Instalando GStreamer y plugins de cámara (libcamerasrc)..."
sudo apt install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libcamera \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev

# 3. Instalar OpenCV SOLO para C++ (sin python3-opencv)
echo "[3/5] Instalando OpenCV para C++ (con soporte GStreamer)..."
sudo apt install -y \
    libopencv-dev \
    opencv-data \
    pkg-config

# 4. Instalar librerías para controlar GPIO desde C++
echo "[4/5] Instalando librerías para control de GPIO..."
# Opción A: libgpiod (El estándar moderno y recomendado en Bookworm)
sudo apt install -y libgpiod-dev gpiod
# Opción B: pigpio (Más antiguo, pero muy fácil de usar)
sudo apt install -y pigpio libpigpio-dev

# 5. Configurar permisos de usuario
echo "[5/5] Configurando permisos de usuario para video y gpio..."
sudo usermod -aG video,gpio,dialout $USER

# Corrección del warning de Zenity
echo "Corrigiendo permisos del directorio de runtime (para Zenity)..."
sudo chmod 700 /run/user/$(id -u) 2>/dev/null || true

echo "=================================================="
echo " ✅ ¡INSTALACIÓN COMPLETADA CON ÉXITO!"
echo "=================================================="
echo "⚠️ IMPORTANTE: Debes REINICIAR tu Raspberry Pi para que"
echo "   los nuevos permisos de grupo (video, gpio) surtan efecto."
echo "   Ejecuta: sudo reboot"
echo "=================================================="
```

# Compilación y ejecución de archivos (codigos del carro)

**DATO IMPORTANTE:** Primero que todo hay que acceder a la carpeta donde están los códigos del carro para iniciarlos. En nuestro caso está escrito así:

```
cd code/LNM/src/visioncontroller
```

## Reto 1
- *Compilación de app.cpp*
```
g++ -O2 app.cpp vision_controller.cpp -o vision_app `pkg-config --cflags --libs opencv4` -lpigpio -pthread -lrt
```

- *Ejecución de app.cpp*
```
sudo -E ./vision_app
```

## Reto 2
- *Compilación de app2.cpp*
```
g++ -O2 app2.cpp vision_controller.cpp -o vision_app2 `pkg-config --cflags --libs opencv4` -lpigpio -pthread -lrt
```

- *Ejecución de app2.cpp*
```
sudo -E ./vision_app2
```

*Dato extra:* Usamos el **bash** para abreviar las lineas de código para compilar y ejecutar juntos y cuando se quiere ejecutar, solo usaremos la linea de ejecución.

# Abreviaciones con Bash

## Reto 1
Creamos un bash escribiendo:

```
nano ./app.sh
```

Ahora hay que escribir:
```
g++ -O2 app.cpp vision_controller.cpp -o vision_app `pkg-config --cflags --libs opencv4` -lpigpio -pthread -lrt
sudo -E ./vision_app
```

Le damos a las teclas *Ctrl+O* y al final *Enter*.

**Al final solo se necesita ejecutar en la terminal ./app2.sh*

## Reto 2
Creamos un bash escribiendo:

```
nano ./app2.sh
```

Ahora hay que escribir:
```
g++ -O2 app2.cpp vision_controller.cpp -o vision_app2 `pkg-config --cflags --libs opencv4` -lpigpio -pthread -lrt
sudo -E ./vision_app2
```

Le damos a las teclas *Ctrl+O* y al final *Enter*.

**Al final solo se necesita ejecutar en la terminal ./app2.sh*
