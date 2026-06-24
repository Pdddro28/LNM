import os
import subprocess
import sys

# --- CONFIGURACIÓN FIJA DE K-O-M-R-A-D ---
USUARIO = os.getlogin()  # Detecta automáticamente 'steven'
RUTA_ENTORNO = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/env/bin/python3.11"
WORKING_DIR = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/"
DIR_SRC = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/src/"

def ejecutar_comando(comando):
    """Ejecuta un comando en la terminal de forma segura."""
    try:
        subprocess.run(comando, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Hubo un error al ejecutar la acción.")
        return False

def escribir_servicio(nombre_servicio, script_python):
    """Genera la plantilla y escribe el archivo del servicio."""
    ruta_destino = f"/etc/systemd/system/{nombre_servicio}"
    ruta_script_completa = os.path.join(DIR_SRC, script_python)

    contenido = f"""[Unit]
Description=Servicio K-O-M-R-A-D: {nombre_servicio}
After=network.target

[Service]
User={USUARIO}
WorkingDirectory={WORKING_DIR}
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/{USUARIO}/.Xauthority
ExecStart={RUTA_ENTORNO} {ruta_script_completa}
Restart=always

[Install]
WantedBy=multi-user.target
"""
    try:
        proceso = subprocess.Popen(['sudo', 'tee', ruta_destino], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        proceso.communicate(input=contenido)
        return True
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")
        return False

def pedir_nombre_servicio():
    nombre = input("\nIntroduce el nombre del servicio (ej. robot_vision): ").strip()
    if not nombre.endswith(".service"):
        nombre += ".service"
    return nombre

# --- FLUJOS DEL MENÚ ---

def crear_servicio():
    print("\n--- 🛠️ CREAR NUEVO SERVICIO ---")
    nombre = pedir_nombre_servicio()
    
    print(f"\nBuscando scripts en la carpeta src: {DIR_SRC}")
    script = input("Nombre del archivo .py a ejecutar (ej. vision_controller.py): ").strip()
    
    if escribir_servicio(nombre, script):
        print("\n⚙️ Configurando el sistema...")
        ejecutar_comando(['sudo', 'systemctl', 'daemon-reload'])
        ejecutar_comando(['sudo', 'systemctl', 'enable', nombre])
        ejecutar_comando(['sudo', 'systemctl', 'start', nombre])
        print(f"\n🚀 ¡Servicio '{nombre}' creado, habilitado e iniciado con éxito!")

def modificar_servicio():
    print("\n--- 📝 MODIFICAR SCRIPT DE UN SERVICIO ---")
    nombre = pedir_nombre_servicio()
    
    if not os.path.exists(f"/etc/systemd/system/{nombre}"):
        print(f"⚠️ El servicio '{nombre}' no existe.")
        return

    script = input("Introduce el nombre del NUEVO archivo .py a ejecutar: ").strip()
    
    print("\nDeteniendo servicio actual para modificar...")
    ejecutar_comando(['sudo', 'systemctl', 'stop', nombre])
    
    if escribir_servicio(nombre, script):
        ejecutar_comando(['sudo', 'systemctl', 'daemon-reload'])
        ejecutar_comando(['sudo', 'systemctl', 'start', nombre])
        print(f"\n🔄 ¡Servicio '{nombre}' actualizado y reiniciado con éxito!")

def deshabilitar_servicio():
    print("\n--- 🛑 DESHABILITAR SERVICIO (Apagar arranque automático) ---")
    nombre = pedir_nombre_servicio()
    if ejecutar_comando(['sudo', 'systemctl', 'stop', nombre]) and ejecutar_comando(['sudo', 'systemctl', 'disable', nombre]):
        print(f"\n🛑 El servicio '{nombre}' se ha detenido y ya NO arrancará al encender la Pi.")

def habilitar_servicio():
    print("\n--- ▶️ HABILITAR SERVICIO (Activar arranque automático) ---")
    nombre = pedir_nombre_servicio()
    if ejecutar_comando(['sudo', 'systemctl', 'enable', nombre]) and ejecutar_comando(['sudo', 'systemctl', 'start', nombre]):
        print(f"\n▶️ El servicio '{nombre}' ahora está activo y arrancará automáticamente.")

def eliminar_servicio():
    print("\n--- 🗑️ ELIMINAR UN SERVICIO ---")
    nombre = pedir_nombre_servicio()
    
    print("Deteniendo y deshabilitando...")
    ejecutar_comando(['sudo', 'systemctl', 'stop', nombre])
    ejecutar_comando(['sudo', 'systemctl', 'disable', nombre])
    
    print("Borrando archivo...")
    if ejecutar_comando(['sudo', 'rm', f"/etc/systemd/system/{nombre}"]):
        ejecutar_comando(['sudo', 'systemctl', 'daemon-reload'])
        ejecutar_comando(['sudo', 'systemctl', 'reset-failed'])
        print(f"\n🗑️ El servicio '{nombre}' ha sido eliminado por completo del sistema.")

# --- MENÚ PRINCIPAL ---

def menu():
    while True:
        print("\n==========================================")
        print("    GESTOR DE SERVICIOS SYSTEMD K-O-M-R-A-D")
        print("==========================================")
        print("A. Crear un servicio")
        print("B. Modificar servicio")
        print("C. Deshabilitar un servicio")
        print("D. Eliminar un servicio")
        print("E. Habilitar un servicio")
        print("S. Salir")
        print("==========================================")
        
        opcion = input("¿Qué deseas hacer?: ").strip().upper()
        
        if opcion == 'A':
            crear_servicio()
        elif opcion == 'B':
            modificar_servicio()
        elif opcion == 'C':
            deshabilitar_servicio()
        elif opcion == 'D':
            eliminar_servicio()
        elif opcion == 'E':
            habilitar_servicio()
        elif opcion == 'S':
            print("\n¡Nos vemos! Éxito con el desarrollo de K-O-M-R-A-D. 🤖")
            break
        else:
            print("⚠️ Opción no válida. Por favor, selecciona una letra de la A a la E (o S para salir).")

if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        print("Este script solo funciona en Linux.")
        sys.exit(1)
    menu()
