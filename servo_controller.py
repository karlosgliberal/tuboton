#!/usr/bin/env python3

from gpiozero import AngularServo
from time import sleep
import sys
from config import SERVO_PIN, SERVO2_PIN

class ServoController:
    def __init__(self):
        self.servo1 = self._setup_servo(SERVO_PIN)
        self.servo2 = self._setup_servo(SERVO2_PIN)
        self.neutral_position = -90
        self.turn_position = 90
        self.neutral_position2 = 30
        self.turn_position2 = 90

    def _setup_servo(self, pin):
        try:
            return AngularServo(
                pin=pin,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
                frame_width=0.02,
                initial_angle=None,
                min_angle=-90,
                max_angle=90
            )
        except Exception as e:
            print("Error al configurar el servo. Asegúrate de que:")
            print("1. Estás ejecutando el script como root (sudo)")
            print("2. El módulo gpiozero está instalado")
            print(f"Error detallado: {str(e)}")
            sys.exit(1)

    def move_servo_smoothly(self, servo, target_angle, steps=5, delay=0.05):
        """Mueve el servo suavemente al ángulo objetivo"""
        try:
            current_angle = servo.angle if servo.angle is not None else -90
            step_size = (target_angle - current_angle) / steps
            
            for i in range(steps):
                servo.angle = current_angle + (step_size * (i + 1))
                sleep(delay)
        except Exception as e:
            print(f"Error al mover el servo: {str(e)}")

    def detach_servo(self, servo):
        """Desactiva el servo estableciendo el ángulo a None"""
        servo.angle = None
        sleep(0.1)

    def move_servo_sequence(self, servo, start_angle, end_angle, steps=5, delay=0.05):
        """Realiza una secuencia de movimientos complejos con el servo"""
        try:
            # Movimiento inicial suave
            self.move_servo_smoothly(servo, end_angle, steps, delay)
            sleep(0.2)
            
            # Movimiento rápido de regreso
            self.move_servo_smoothly(servo, start_angle, 3, 0.02)
            sleep(0.1)
            
            # Movimiento intermedio
            self.move_servo_smoothly(servo, (start_angle + end_angle) / 2, 2, 0.03)
            sleep(0.1)
            
            # Secuencia de vibración
            for _ in range(5):
                servo.angle = end_angle
                sleep(0.05)
                servo.angle = start_angle
                sleep(0.05)
            
            # Posición final
            servo.angle = start_angle
            sleep(0.1)
            
        except Exception as e:
            print(f"Error en la secuencia del servo: {str(e)}")

    def perform_button_press_sequence(self):
        """Realiza la secuencia completa de movimiento cuando se presiona el botón"""
        # Mover el primer servo normalmente
        self.move_servo_smoothly(self.servo1, self.turn_position)
        # Realizar la secuencia compleja con el segundo servo
        self.move_servo_smoothly(self.servo2, self.neutral_position2, self.turn_position2)
        sleep(1)  # Breve pausa para mantener el giro
        self.move_servo_smoothly(self.servo1, self.neutral_position)
        self.move_servo_smoothly(self.servo2, self.neutral_position2)
        self.detach_servo(self.servo1)
        self.detach_servo(self.servo2)

    def cleanup(self):
        """Limpia los recursos de los servos"""
        self.detach_servo(self.servo1)
        self.detach_servo(self.servo2) 