import time

class TemporizadorNoBloqueante:
    def __init__(self, intervalo_segundos):
        self.intervalo = intervalo_segundos
        self.tiempo_ultimo = time.time()
        self.activo = False

    def iniciar(self):
        """Inicia o reinicia el temporizador."""
        self.tiempo_ultimo = time.time()
        self.activo = True

    def ha_expirado(self):
        """
        Consulta si ya pas� el tiempo programado.
        Devuelve True SOLO en el instante en que expira y reinicia su estado.
        """
        if self.activo and (time.time() - self.tiempo_ultimo >= self.intervalo):
            self.activo = False
            return True
        return False

    def esta_transcurriendo(self):
        """Devuelve True mientras el tiempo siga corriendo."""
        return self.activo and (time.time() - self.tiempo_ultimo < self.intervalo)