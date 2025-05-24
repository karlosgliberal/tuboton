#!/usr/bin/env python3

import time
from gpiozero import Button
from config import BUTTON_PIN, SOLO_BOTON, DEBUG_MODE
from servo_controller import ServoController
from printer_controller import PrinterController
from display_controller import DisplayController

class TuBoton:
    def __init__(self):
        # Inicializar controladores
        self.servo_controller = ServoController()
        self.display_controller = DisplayController()
        self.printer_controller = PrinterController() if not SOLO_BOTON else None
        self.button = Button(BUTTON_PIN)
        
        # Variables de estado
        self.servo_timer = None
        self.servo_state = "neutral"
        print("Sistema inicializado correctamente")

    def handle_button_press(self):
        """Maneja el evento de presionar el botón"""
        current_time = time.time()
        
        # 1. Seleccionar y mostrar la imagen
        current_image = self.printer_controller.get_random_image() if self.printer_controller else "images/imagen_35.png"
        self.display_controller.show_image(current_image)
        print("Pulsador presionado - Mostrando imagen")
        
        # 2. Imprimir el ticket si no estamos en modo SOLO_BOTON
        if self.printer_controller:
            print("Imprimiendo ticket...")
            if DEBUG_MODE:
                self.printer_controller.print_debug()
            else:
                self.printer_controller.print_art_ticket()
        
        # 3. Manejar los servos según el modo
        if SOLO_BOTON:
            self.servo_controller.perform_button_press_sequence()
            self.display_controller.set_hide_time(current_time + 2)
        else:
            self.servo_timer = current_time
            self.servo_state = "waiting"
            print("Iniciando temporizador para servo...")

    def handle_servo_states(self):
        """Maneja los estados de los servos en modo normal"""
        if not SOLO_BOTON and self.servo_timer is not None:
            current_time = time.time()
            
            if self.servo_state == "waiting" and current_time - self.servo_timer >= 4:
                # Mover ambos servos a posición de giro
                self.servo_controller.move_servo_smoothly(self.servo_controller.servo1, self.servo_controller.turn_position)
                self.servo_controller.move_servo_smoothly(self.servo_controller.servo2, self.servo_controller.turn_position)
                self.servo_state = "turning"
                self.servo_timer = current_time
                
            elif self.servo_state == "turning" and current_time - self.servo_timer >= 2:
                # Volver ambos servos a posición neutral
                self.servo_controller.move_servo_smoothly(self.servo_controller.servo1, self.servo_controller.neutral_position)
                self.servo_controller.move_servo_smoothly(self.servo_controller.servo2, self.servo_controller.neutral_position)
                self.servo_controller.detach_servo(self.servo_controller.servo1)
                self.servo_controller.detach_servo(self.servo_controller.servo2)
                self.servo_state = "returning"
                self.servo_timer = current_time
                
            elif self.servo_state == "returning" and current_time - self.servo_timer >= 0.5:
                # Establecer el tiempo para ocultar la imagen (5 segundos después)
                self.display_controller.set_hide_time(current_time + 5)
                self.servo_timer = None
                self.servo_state = "neutral"

    def run(self):
        """Ejecuta el bucle principal del programa"""
        try:
            while True:
                # Manejar eventos de Pygame
                if not self.display_controller.handle_events():
                    break

                current_time = time.time()
                
                # Verificar si el botón físico está presionado
                if self.button.is_pressed:
                    self.handle_button_press()
                
                # Manejar estados del servo
                self.handle_servo_states()
                
                # Verificar si es hora de ocultar la imagen
                self.display_controller.should_hide_image(current_time)
                
                # Actualizar la pantalla
                self.display_controller.update_display()

        except KeyboardInterrupt:
            print("\nPrograma detenido por el usuario")
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpia todos los recursos"""
        self.servo_controller.cleanup()
        if self.printer_controller:
            self.printer_controller.cleanup()
        self.display_controller.cleanup()

if __name__ == "__main__":
    app = TuBoton()
    app.run() 