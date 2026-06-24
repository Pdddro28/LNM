import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# --- CONFIGURACIÓN ESTÁTICA K-O-M-R-A-D ---
USUARIO = os.getlogin()
RUTA_ENTORNO = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/env/bin/python3.11"
WORKING_DIR = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/"
DIR_SRC = f"/home/{USUARIO}/Documents/K-O-M-R-A-D/src/"

# Configuración de apariencia de CustomTkinter
ctk.set_appearance_mode("System")  # Cambia con el sistema (Light/Dark)
ctk.set_default_color_theme("blue")

class GestorServiciosGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestor de Servicios Systemd - K-O-M-R-A-D")
        self.geometry("600x550")
        self.resizable(False, False)

        # --- TÍTULO PRINCIPAL ---
        self.titulo = ctk.CTkLabel(self, text="🤖 Panel de Control de Servicios", font=ctk.CTkFont(size=22, weight="bold"))
        self.titulo.pack(pady=20)

        # --- MARCO DE DATOS ---
        self.frame_datos = ctk.CTkFrame(self)
        self.frame_datos.pack(pady=10, padx=30, fill="x")

        self.lbl_nombre = ctk.CTkLabel(self.frame_datos, text="Nombre del Servicio:", font=ctk.CTkFont(weight="bold"))
        self.lbl_nombre.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_nombre = ctk.CTkEntry(self.frame_datos, placeholder_text="ej. mi_servicio_vision", width=250)
        self.entry_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.lbl_script = ctk.CTkLabel(self.frame_datos, text="Script Python (.py):", font=ctk.CTkFont(weight="bold"))
        self.lbl_script.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.btn_buscar = ctk.CTkButton(self.frame_datos, text="🔍 Buscar Script", command=self.buscar_archivo, width=120)
        self.btn_buscar.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.lbl_ruta_seleccionada = ctk.CTkLabel(self.frame_datos, text="Ningún archivo seleccionado", text_color="gray")
        self.lbl_ruta_seleccionada.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # --- MARCO DE ACCIONES ---
        self.frame_acciones = ctk.CTkLabelFrame(self, text=" Acciones del Sistema ")
        self.frame_acciones.pack(pady=20, padx=30, fill="both", expand=True)

        # Configurar columnas del contenedor de botones
        self.frame_acciones.grid_columnconfigure(0, weight=1)
        self.frame_acciones.grid_columnconfigure(1, weight=1)

        # Botones de Acción
        self.btn_crear = ctk.CTkButton(self.frame_acciones, text="⚙️ Crear / Instalar", fg_color="#2ecc71", hover_color="#27ae60", command=self.crear_servicio)
        self.btn_crear.grid(row=0, column=0, padx=20, pady=15, sticky="ew")

        self.btn_modificar = ctk.CTkButton(self.frame_acciones, text="📝 Modificar Script", fg_color="#3498db", hover_color="#2980b9", command=self.modificar_servicio)
        self.btn_modificar.grid(row=0, column=1, padx=20, pady=15, sticky="ew")

        self.btn_habilitar = ctk.CTkButton(self.frame_acciones, text="▶️ Activar Auto-Arranque", fg_color="#1abc9c", hover_color="#16a085", command=self.habilitar_servicio)
        self.btn_habilitar.grid(row=1, column=0, padx=20, pady=15, sticky="ew")

        self.btn_deshabilitar = ctk.CTkButton(self.frame_acciones, text="🛑 Pausar / Deshabilitar", fg_color="#e67e22", hover_color="#d35400", command=self.deshabilitar_servicio)
        self.btn_deshabilitar.grid(row=1, column=1, padx=20, pady=15, sticky="ew")

        self.btn_eliminar = ctk.CTkButton(self.frame_acciones, text="🗑️ Eliminar por Completo", fg_color="#e74c3c", hover_color="#c0392b", command=self.eliminar_servicio)
        self.btn_eliminar.grid(row=2, column=0, columnspan=2, padx=20, pady=15)

        self.script_elegido = ""

    # --- LÓGICA DE INTERFAZ ---

    def buscar_archivo(self):
        # Abre el explorador directamente en la carpeta src de K-O-M-R-A-D
        archivo = filedialog.askopenfilename(
            initialdir=DIR_SRC,
            title="Selecciona el Script de K-O-M-R-A-D",
            filetypes=(("Archivos Python", "*.py"), ("Todos los archivos", "*.*"))
        )
        if archivo:
            self.script_elegido = archivo
            nombre_archivo = os.path.basename(archivo)
            self.lbl_ruta_seleccionada.configure(text=f"Seleccionado: src/{nombre_archivo}", text_color="#2ecc71")

    def obtener_nombre(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Faltan datos", "Por favor, introduce un nombre para el servicio.")
            return None
        if not nombre.endswith(".service"):
            nombre += ".service"
        return nombre

    def ejecutar_comando_silencioso(self, comando):
        try:
            subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def guardar_servicio_archivo(self, nombre_servicio):
        ruta_destino = f"/etc/systemd/system/{nombre_servicio}"
        contenido = f"""[Unit]
Description=Servicio Grafico K-O-M-R-A-D: {nombre_servicio}
After=network.target

[Service]
User={USUARIO}
WorkingDirectory={WORKING_DIR}
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/{USUARIO}/.Xauthority
ExecStart={RUTA_ENTORNO} {self.script_elegido}
Restart=always

[Install]
WantedBy=multi-user.target
"""
        try:
            proceso = subprocess.Popen(['sudo', 'tee', ruta_destino], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            proceso.communicate(input=contenido)
            return True
        except Exception as e:
            messagebox.showerror("Error de Escritura", f"No se pudo guardar el archivo: {e}")
            return False

    # --- ACCIONES DEL SYSTEMD ---

    def crear_servicio(self):
        nombre = self.obtener_nombre()
        if not nombre: return
        if not self.script_elegido:
            messagebox.showwarning("Faltan datos", "Por favor, busca y selecciona un script .py primero.")
            return

        if self.guardar_servicio_archivo(nombre):
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'daemon-reload'])
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'enable', nombre])
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'start', nombre])
            messagebox.showinfo("¡Éxito!", f"Servicio '{nombre}' creado, habilitado e iniciado.")

    def modificar_servicio(self):
        nombre = self.obtener_nombre()
        if not nombre: return
        if not os.path.exists(f"/etc/systemd/system/{nombre}"):
            messagebox.showerror("No existe", f"El servicio '{nombre}' no se encuentra registrado.")
            return
        if not self.script_elegido:
            messagebox.showwarning("Faltan datos", "Selecciona el nuevo script .py para este servicio.")
            return

        self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'stop', nombre])
        if self.guardar_servicio_archivo(nombre):
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'daemon-reload'])
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'start', node])
            messagebox.showinfo("¡Actualizado!", f"El servicio '{nombre}' ahora ejecuta el nuevo script.")

    def habilitar_servicio(self):
        nombre = self.obtener_nombre()
        if not nombre: return
        if self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'enable', nombre]) and self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'start', nombre]):
            messagebox.showinfo("Habilitado", f"El servicio '{nombre}' arrancará automáticamente en cada inicio.")

    def deshabilitar_servicio(self):
        nombre = self.obtener_nombre()
        if not nombre: return
        if self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'stop', nombre]) and self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'disable', nombre]):
            messagebox.showinfo("Deshabilitado", f"El servicio '{nombre}' se detuvo y ya no iniciará al encender la Pi.")

    def eliminar_servicio(self):
        nombre = self.obtener_nombre()
        if not nombre: return
        
        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas borrar por completo '{nombre}'?")
        if confirmar:
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'stop', nombre])
            self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'disable', nombre])
            if self.ejecutar_comando_silencioso(['sudo', 'rm', f"/etc/systemd/system/{nombre}"]):
                self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'daemon-reload'])
                self.ejecutar_comando_silencioso(['sudo', 'systemctl', 'reset-failed'])
                messagebox.showinfo("Eliminado", f"El servicio '{nombre}' ha sido borrado del sistema.")

if __name__ == "__main__":
    app = GestorServiciosGUI()
    app.mainloop()
