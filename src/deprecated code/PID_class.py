class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.prev_error = 0
        self.integral = 0

        self.error = 0

    def compute(self, setpoint, current_value):
        # Calcular error
        self.error = setpoint - current_value
        
        # T�rmino Proporcional
        p_term = self.kp * self.error
        
        # T�rmino Integral
        self.integral += self.error
        i_term = self.ki * self.integral
        
        # T�rmino Derivativo
        derivative = self.error - self.prev_error
        d_term = self.kd * derivative
        
        # Guardar error para la siguiente iteraci�n
        self.prev_error = self.error
        
        # Salida total
        output = p_term + i_term + d_term
        return output

    def reset(self):
        self.prev_error = 0
        self.integral = 0