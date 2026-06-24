import cv2 as cv
import numpy as np
import time
from mega_pi_controller import MegaPiController

def comprobar_atasco_visual():
    # Inicializamos el controlador del carro
    # NOTA: Asegúrate de que en tu constructor de MegaPiController ya llamaste a self.camera.start()
    LNM = MegaPiController("/dev/ttyUSB0", 115200)
    
    print("🚗 Iniciando test de detección de atasco visual...")
    time.sleep(1)
    
    # 1. Arrancar el movimiento del carro
    LNM.move_forward(speed=35)
    
    # 2. Capturar el primer fotograma de referencia
    LNM.vision.receive_image()
    if LNM.vision.frame is None:
        print("❌ Error: No se puede acceder a la cámara. Abortando.")
        LNM.stop()
        return

    # Convertimos a escala de grises para que el cálculo sea ultrarrápido
    prev_frame = cv.cvtColor(LNM.vision.frame, cv.COLOR_BGR2GRAY)
    
    # Variables de control del "freno de mano"
    UMBRAL_CAMBIO_PIXELS = 150000  # Cuántos píxeles cambiaron (sensibilidad al movimiento)
    TIEMPO_MAXIMO_ESTATICO = 1.5   # Segundos permitidos sin movimiento antes de activar el freno
    
    ultima_vez_con_movimiento = time.time()
    running = True

    try:
        while running:
            # Capturar el fotograma actual
            LNM.vision.receive_image()
            if LNM.vision.frame is None:
                continue
                
            current_frame = cv.cvtColor(LNM.vision.frame, cv.COLOR_BGR2GRAY)
            
            # Calcular la diferencia absoluta entre el frame anterior y el actual
            frame_diff = cv.absdiff(current_frame, prev_frame)
            
            # Aplicar un umbral para eliminar el ruido estático de la cámara
            _, thresh = cv.threshold(frame_diff, 25, 255, cv.THRESH_BINARY)
            
            # Contar cuántos píxeles cambiaron realmente
            pixels_cambiados = np.sum(thresh == 255)
            
            tiempo_actual = time.time()
            
            # Monitorear el movimiento en la terminal
            print(f"Píxeles en movimiento: {pixels_cambiados} | Tiempo estático: {round(tiempo_actual - ultima_vez_con_movimiento, 2)}s", end='\r')
            
            # Si hay suficiente cambio en los píxeles, el carro se está moviendo en el mundo real
            if pixels_cambiados > UMBRAL_CAMBIO_PIXELS:
                ultima_vez_con_movimiento = tiempo_actual
            else:
                # Si el carro pasa más tiempo del permitido sin reportar cambios visuales...
                if (tiempo_actual - ultima_vez_con_movimiento) > TIEMPO_MAXIMO_ESTATICO:
                    print("\n\n🚨 ¡FRENO DE MANO ACTIVADO! El carro está físicamente atrapado.")
                    LNM.stop()
                    
                    # Mostrar el último frame de la captura del atasco
                    cv.putText(LNM.vision.frame, "EMERGENCY BRAKE - STUCK", (50, 50), 
                               cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv.imshow("Deteccion de Atasco", LNM.vision.frame)
                    cv.waitKey(0) # Bloquear aquí para inspección visual
                    break
            
            # Dibujar un feed visual para calibrar la sensibilidad
            #cv.imshow("Diferencia de Movimiento (Binaria)", thresh)
            
            # Actualizar el frame anterior para la siguiente iteración
            prev_frame = current_frame
            
            # Salida segura con 'q'
            #if cv.waitKey(1) & 0xFF == ord('q'):
                #break
                
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario.")
    finally:
        LNM.stop()
        cv.destroyAllWindows()
        print("\nScript finalizado de forma segura.")

if __name__ == "__main__":
    comprobar_atasco_visual()
