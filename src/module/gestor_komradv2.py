import os
import subprocess
import sys

# --- CONFIGURACIÓN FIJA DE K-O-M-R-A-D ---
USUARIO = os.getlogin()
WORKING_DIR = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/"
DIR_SRC = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/src/"
REGISTRO_SERVICIOS = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/servicios_registrados.txt"

# ============================================
# GESTIÓN DEL REGISTRO DE SERVICIOS (TXT)
# ============================================

def cargar_registro():
    """Carga el archivo de registro de servicios. Retorna un diccionario."""
    registro = {}
    if os.path.exists(REGISTRO_SERVICIOS):
        with open(REGISTRO_SERVICIOS, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if linea and ':' in linea:
                    nombre, ruta = linea.split(':', 1)
                    registro[nombre.strip()] = ruta.strip()
    return registro

def guardar_registro(registro):
    """Guarda el diccionario de servicios en el archivo de registro."""
    with open(REGISTRO_SERVICIOS, 'w') as f:
        for nombre, ruta in registro.items():
            f.write(f"{nombre}:{ruta}\n")

def registrar_servicio(nombre_servicio, ruta_binario):
    """Añade o actualiza un servicio en el registro."""
    registro = cargar_registro()
    registro[nombre_servicio] = ruta_binario
    guardar_registro(registro)

def desregistrar_servicio(nombre_servicio):
    """Elimina un servicio del registro."""
    registro = cargar_registro()
    if nombre_servicio in registro:
        del registro[nombre_servicio]
        guardar_registro(registro)
        return True
    return False

def servicio_en_registro(nombre_servicio):
    """Verifica si un servicio fue creado por este script."""
    registro = cargar_registro()
    return nombre_servicio in registro

# ============================================
# BÚSQUEDA DE BINARIOS EN SRC
# ============================================

def buscar_binarios_en_src():
    """Busca archivos ejecutables compilados en la carpeta src y subcarpetas."""
    binarios = []
    
    if not os.path.exists(DIR_SRC):
        print(f"⚠️ La carpeta '{DIR_SRC}' no existe.")
        return binarios
    
    for raiz, dirs, archivos in os.walk(DIR_SRC):
        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            
            # Verificar que es ejecutable y no tiene extensión de código fuente
            extensiones_ignorar = {'.cpp', '.h', '.hpp', '.c', '.py', '.txt', '.md', '.json', '.o', '.a'}
            _, ext = os.path.splitext(archivo)
            
            if ext.lower() in extensiones_ignorar:
                continue
            
            # Verificar que tiene permisos de ejecución
            if os.access(ruta_completa, os.X_OK):
                # Verificar que es un binario ELF (ejecutable de Linux)
                try:
                    with open(ruta_completa, 'rb') as f:
                        magic = f.read(4)
                        if magic == b'\x7fELF':
                            binarios.append(ruta_completa)
                except (IOError, PermissionError):
                    continue
    
    return binarios

def mostrar_y_seleccionar_binario():
    """Muestra los binarios disponibles y retorna la ruta seleccionada."""
    binarios = buscar_binarios_en_src()
    
    if not binarios:
        print("❌ No se encontraron binarios compilados en la carpeta src.")
        print("💡 Compila tu código primero con:")
        print(f"   g++ -std=c++17 -O2 src/archivo.cpp -o src/binario `pkg-config --cflags --libs opencv4`")
        return None
    
    print(f"\n📦 Binarios encontrados en '{DIR_SRC}':")
    print("-" * 60)
    
    for i, binario in enumerate(binarios, 1):
        # Mostrar ruta relativa para mayor legibilidad
        ruta_relativa = os.path.relpath(binario, WORKING_DIR)
        print(f"  [{i}] {ruta_relativa}")
    
    print("-" * 60)
    
    while True:
        try:
            seleccion = int(input(f"Selecciona un binario (1-{len(binarios)}): ").strip())
            if 1 <= seleccion <= len(binarios):
                ruta_seleccionada = binarios[seleccion - 1]
                print(f"✅ Seleccionado: {ruta_seleccionada}")
                return ruta_seleccionada
            else:
                print(f"⚠️ Número fuera de rango. Ingresa un número entre 1 y {len(binarios)}.")
        except ValueError:
            print("⚠️ Ingresa un número válido.")

# ============================================
# UTILIDADES
# ============================================

def ejecutar_comando(comando):
    """Ejecuta un comando en la terminal de forma segura."""
    try:
        subprocess.run(comando, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Hubo un error al ejecutar la acción.")
        return False

def escribir_servicio(nombre_servicio, ruta_binario):
    """Genera la plantilla y escribe el archivo del servicio systemd."""
    ruta_destino = f"/etc/systemd/system/{nombre_servicio}"

    contenido = f"""[Unit]
Description=Servicio K-O-M-R-A-D: {nombre_servicio}
After=network.target

[Service]
User={USUARIO}
WorkingDirectory={WORKING_DIR}
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/{USUARIO}/.Xauthority
ExecStart={ruta_binario}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    try:
        proceso = subprocess.Popen(
            ['sudo', 'tee', ruta_destino],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        proceso.communicate(input=contenido)
        return True
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")
        return False

def pedir_nombre_servicio():
    """Pide al usuario el nombre del servicio."""
    nombre = input("\nIntroduce el nombre del servicio (ej. robot_vision): ").strip()
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return None
    if not nombre.endswith(".service"):
        nombre += ".service"
    return nombre

def pedir_nombre_servicio_existente():
    """Pide al usuario que seleccione un servicio del registro."""
    registro = cargar_registro()
    
    if not registro:
        print("⚠️ No hay servicios registrados por K-O-M-R-A-D.")
        return None
    
    print("\n📋 Servicios registrados por K-O-M-R-A-D:")
    print("-" * 60)
    
    servicios_lista = list(registro.keys())
    for i, nombre in enumerate(servicios_lista, 1):
        ruta = registro[nombre]
        ruta_relativa = os.path.relpath(ruta, WORKING_DIR) if ruta.startswith(WORKING_DIR) else ruta
        print(f"  [{i}] {nombre} → {ruta_relativa}")
    
    print("-" * 60)
    
    while True:
        try:
            seleccion = int(input(f"Selecciona un servicio (1-{len(servicios_lista)}): ").strip())
            if 1 <= seleccion <= len(servicios_lista):
                nombre_seleccionado = servicios_lista[seleccion - 1]
                print(f"✅ Seleccionado: {nombre_seleccionado}")
                return nombre_seleccionado
            else:
                print(f"⚠️ Número fuera de rango. Ingresa un número entre 1 y {len(servicios_lista)}.")
        except ValueError:
            print("⚠️ Ingresa un número válido.")

# ============================================
# FLUJOS DEL MENÚ
# ============================================

def crear_servicio():
    print("\n--- 🛠️ CREAR NUEVO SERVICIO ---")
    
    # 1. Pedir nombre del servicio
    nombre = pedir_nombre_servicio()
    if nombre is None:
        return
    
    # Verificar si ya existe en el registro
    if servicio_en_registro(nombre):
        print(f"⚠️ El servicio '{nombre}' ya está registrado.")
        confirmacion = input("¿Deseas sobrescribirlo? (s/n): ").strip().lower()
        if confirmacion != 's':
            print("Operación cancelada.")
            return
    
    # 2. Seleccionar binario de la lista
    ruta_binario = mostrar_y_seleccionar_binario()
    if ruta_binario is None:
        return
    
    # 3. Crear el archivo de servicio
    if escribir_servicio(nombre, ruta_binario):
        # 4. Registrar en el txt
        registrar_servicio(nombre, ruta_binario)
        
        # 5. Configurar systemd
        print("\n⚙️ Configurando el sistema...")
        ejecutar_comando(['sudo', 'systemctl', 'daemon-reload'])
        ejecutar_comando(['sudo', 'systemctl', 'enable', nombre])
        ejecutar_comando(['sudo', 'systemctl', 'start', nombre])
        
        print(f"\n🚀 ¡Servicio '{nombre}' creado, habilitado e iniciado con éxito!")
        print(f"📦 Binario: {ruta_binario}")
        print(f"📝 Registrado en: {REGISTRO_SERVICIOS}")

def modificar_servicio():
    print("\n--- 📝 MODIFICAR BINARIO DE UN SERVICIO ---")
    
    # Seleccionar servicio del registro
    nombre = pedir_nombre_servicio_existente()
    if nombre is None:
        return
    
    # Seleccionar nuevo binario
    ruta_binario = mostrar_y_seleccionar_binario()
    if ruta_binario is None:
        return
    
    print(f"\nDeteniendo servicio '{nombre}' para modificar...")
    ejecutar_comando(['sudo', 'systemctl', 'stop', nombre])
    
    if escribir_servicio(nombre, ruta_binario):
        # Actualizar registro
        registrar_servicio(nombre, ruta_binario)
        
        ejecutar_comando(['sudo', 'systemctl', 'daemon-reload'])
        ejecutar_comando(['sudo', 'systemctl', 'start', nombre])
        print(f"\n🔄 ¡Servicio '{nombre}' actualizado y reiniciado con éxito!")
        print(f"📦 Nuevo binario: {ruta_binario}")

def deshabilitar_servicio():
    print("\n--- 🛑 DESHABILITAR SERVICIO (Apagar arranque automático) ---")
    
    nombre = pedir_nombre_servicio_existente()
    if nombre is None:
        return
    
    if ejecutar_comando(['sudo', 'systemctl', 'stop', nombre]) and \
       ejecutar_comando(['sudo', 'systemctl', 'disable', nombre]):
        print(f"\n🛑 El servicio '{nombre}' se ha detenido y ya NO arrancará al encender la Pi.")

def habilitar_servicio():
    print("\n--- ▶️ HABILITAR SERVICIO (Activar arranque automático) ---")
    
    nombre = pedir_nombre_servicio_existente()
    if nombre is None:
        return
    
    if ejecutar_comando(['sudo', 'systemctl', 'enable', nombre]) and \
       ejecutar_comando(['sudo', 'systemctl', 'start', nombre]):
        print(f"\n▶️ El servicio '{nombre}' ahora está activo y arrancará automáticamente.")

def eliminar_servicio():
    print("\n--- 🗑️ ELIMINAR UN SERVICIO ---")
    print("⚠️ Solo puedes eliminar servicios registrados por K-O-M-R-A-D.")
    
    nombre = pedir_nombre_servicio_existente()
    if nombre is None:
        return
    
    # Confirmación de seguridad
    confirmacion = input(f"\n¿Estás seguro de eliminar '{nombre}'? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Operación cancelada.")
        return
    
    print("Deteniendo y deshabilitando...")
    ejecutar_comando(['sudo', 'systemctl', 'stop', nombre])
    ejecutar_comando(['sudo', 'systemctl', 'disable', nombre])
    
    print("Borrando archivo de servicio...")
    if ejecutar_comando(['sudo', 'rm', f"/etc/systemd/system/{nombre}"]):
        ejecutar_comando(['sudo', 'systemctl', 'daemon-reload'])
        ejecutar_comando(['sudo', 'systemctl', 'reset-failed'])
        
        # Eliminar del registro
        desregistrar_servicio(nombre)
        
        print(f"\n🗑️ El servicio '{nombre}' ha sido eliminado por completo del sistema.")
        print(f"📝 Eliminado del registro: {REGISTRO_SERVICIOS}")

def listar_servicios():
    """Lista los servicios registrados por K-O-M-R-A-D con su estado."""
    print("\n--- 📋 SERVICIOS REGISTRADOS POR K-O-M-R-A-D ---")
    
    registro = cargar_registro()
    
    if not registro:
        print("  No hay servicios registrados.")
        return
    
    print(f"{'SERVICIO':<30} {'BINARIO':<40} {'ESTADO'}")
    print("-" * 90)
    
    for nombre, ruta in registro.items():
        # Obtener estado del servicio
        try:
            resultado = subprocess.run(
                ['systemctl', 'is-active', nombre],
                capture_output=True, text=True
            )
            estado = resultado.stdout.strip()
        except:
            estado = "desconocido"
        
        ruta_relativa = os.path.relpath(ruta, WORKING_DIR) if ruta.startswith(WORKING_DIR) else ruta
        
        # Icono según estado
        icono = "🟢" if estado == "active" else "🔴" if estado == "inactive" else "🟡"
        
        print(f"  {icono} {nombre:<28} {ruta_relativa:<38} {estado}")
    
    print(f"\n📁 Registro guardado en: {REGISTRO_SERVICIOS}")

# ============================================
# MENÚ PRINCIPAL
# ============================================

def menu():
    while True:
        print("\n==========================================")
        print("    GESTOR DE SERVICIOS SYSTEMD K-O-M-R-A-D")
        print("==========================================")
        print("A. Crear un servicio")
        print("B. Modificar servicio (cambiar binario)")
        print("C. Deshabilitar un servicio")
        print("D. Eliminar un servicio")
        print("E. Habilitar un servicio")
        print("F. Listar servicios registrados")
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
        elif opcion == 'F':
            listar_servicios()
        elif opcion == 'S':
            print("\n¡Nos vemos! Éxito con el desarrollo de K-O-M-R-A-D. 🤖")
            break
        else:
            print("⚠️ Opción no válida. Por favor, selecciona una letra de la A a la F (o S para salir).")

if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        print("Este script solo funciona en Linux.")
        sys.exit(1)
    menu()