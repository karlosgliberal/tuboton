#!/usr/bin/env python3

import time
import uuid
import datetime
import usb.core
import usb.util
from escpos.printer import Usb
from PIL import Image, ImageEnhance, ImageOps
import glob
import random
import os
from gpiozero import AngularServo, Button
import sys
from time import sleep
import pygame

# --- Configuración de la Impresora ---
VENDOR_ID = 0x0416
PRODUCT_ID = 0x5011

# --- Configuración de Debug ---
DEBUG_MODE = False    # Cambia a False para modo normal

# --- Configuración Solo Botón ---
SOLO_BOTON = False # Si es True, la impresora no se inicializa ni se usa

# --- Configuración del Servo ---
SERVO_PIN = 18
BUTTON_PIN = 17
SERVO2_PIN = 21  # Nuevo pin para el segundo servo

# --- Configuración de Pygame ---
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Tu Botón")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Configuración del botón en pantalla
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 100
BUTTON_X = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
BUTTON_Y = (SCREEN_HEIGHT - BUTTON_HEIGHT) // 2

BUTTON_STYLES = {
    "Airbnb": {
        "desc": "soft, rounded, warm, modern startup",
        "ref": "Airbnb's design system",
        "style_text": "soft, welcoming, modern startup UI",
        "prompt": "Use a soft, friendly, modern style with rounded corners, subtle shadows, and warm colors. Follow the visual language of Airbnb's design system."
    },
    "IBM": {
        "desc": "minimal, high-contrast, square",
        "ref": "IBM Carbon Design",
        "style_text": "minimal, high-contrast, enterprise-grade",
        "prompt": "Use a minimalistic, professional style with strong contrast and square edges. Follow IBM Carbon Design principles."
    },
    "Material Design": {
        "desc": "elevated, colorful accents",
        "ref": "Material Design 3",
        "style_text": "material, elevated, colorful accents",
        "prompt": "Use Material Design principles with elevation, rounded corners, and clear typography. Include color hierarchy according to Google's style."
    },
    "iOS": {
        "desc": "flat, clean, rounded, soft",
        "ref": "iOS Human Interface",
        "style_text": "clean, flat, rounded, soft shadows",
        "prompt": "Use a sleek, rounded style with soft gradients or shadows and minimalistic type. Mimic Apple's iOS design aesthetic."
    },
    "Fantasy RPG": {
        "desc": "ornate, textured, medieval",
        "ref": "Fantasy UI",
        "style_text": "ornate, textured, medieval style",
        "prompt": "Use an ornate style with fantasy elements, embossed borders, and textured materials like leather, stone, or gold. Inspired by medieval RPG interfaces."
    },
    "Cyberpunk": {
        "desc": "neon, angular, futuristic",
        "ref": "High-tech UI",
        "style_text": "neon, futuristic, angular",
        "prompt": "Use a neon-lit, high-tech style with angular shapes, dark backgrounds, and glowing edges. Inspired by cyberpunk sci-fi aesthetics."
    },
    "Kids App": {
        "desc": "playful, bright, bold shapes",
        "ref": "Educational Apps",
        "style_text": "playful, bright, soft shapes",
        "prompt": "Use playful, colorful shapes with bold fonts, pill buttons, and cheerful tones. Designed for a children's mobile app."
    },
    "Luxury Brand": {
        "desc": "elegant, serif, muted tones",
        "ref": "High-end Fashion UI",
        "style_text": "elegant, muted, serif typography",
        "prompt": "Use a minimal and luxurious aesthetic with serif fonts, high contrast, and refined spacing. Inspired by luxury e-commerce platforms."
    },
    "Brutalist": {
        "desc": "raw, flat, stark",
        "ref": "Brutalist Web",
        "style_text": "raw, stark, flat",
        "prompt": "Use a flat, bold style with harsh borders, basic system fonts, and monochromatic schemes. Inspired by brutalist web interfaces."
    },
    "Neumorphism": {
        "desc": "soft, embossed, extruded",
        "ref": "Neo-Skeuomorphic",
        "style_text": "soft, extruded, tactile UI",
        "prompt": "Use soft light and shadow to create a tactile, extruded button appearance on a monochrome background. Inspired by neumorphic design."
    },
    "Metro": {
        "desc": "flat, colorful tiles",
        "ref": "MS Metro",
        "style_text": "flat, bold, colorful tile-based UI",
        "prompt": "Use flat UI blocks, bold sans-serif typography, and strong contrasting colors. Inspired by Microsoft Metro design for Windows 8."
    },
    "Minimal Web3": {
        "desc": "glassmorphism, gradients",
        "ref": "Web3 Dash",
        "style_text": "glassmorphic, soft gradient, Web3 style",
        "prompt": "Use translucent cards, pastel gradients, and glowing elements. Inspired by futuristic Web3 UI styles seen in crypto dashboards."
    }
}

def get_random_style():
    """Selecciona un estilo aleatorio del diccionario de estilos."""
    style_name = random.choice(list(BUTTON_STYLES.keys()))
    return style_name, BUTTON_STYLES[style_name]

def setup_servo(pin=SERVO_PIN):
    try:
        servo = AngularServo(
            pin=pin,
            min_pulse_width=0.0005,
            max_pulse_width=0.0025,
            frame_width=0.02,
            initial_angle=None,
            min_angle=-90,
            max_angle=90
        )
        return servo
    except Exception as e:
        print("Error al configurar el servo. Asegúrate de que:")
        print("1. Estás ejecutando el script como root (sudo)")
        print("2. El módulo gpiozero está instalado")
        print(f"Error detallado: {str(e)}")
        sys.exit(1)

def move_servo_smoothly(servo, target_angle, steps=5, delay=0.05):
    """Mueve el servo suavemente al ángulo objetivo"""
    try:
        current_angle = servo.angle if servo.angle is not None else -90
        step_size = (target_angle - current_angle) / steps
        
        for i in range(steps):
            servo.angle = current_angle + (step_size * (i + 1))
            sleep(delay)
    except Exception as e:
        print(f"Error al mover el servo: {str(e)}")

def detach_servo(servo):
    """Desactiva el servo estableciendo el ángulo a None"""
    servo.angle = None
    time.sleep(0.1)

def setup_printer():
    try:
        printer = Usb(VENDOR_ID, PRODUCT_ID, timeout=0, in_ep=0x81, out_ep=0x01)
        return printer
    except usb.core.USBError as e:
        if e.errno == 13:
            print("\n*** ERROR DE PERMISOS USB ***")
            print("Asegúrate de que tu usuario tiene permisos para acceder al dispositivo USB.")
        elif e.errno == 19:
            print(f"\n*** ERROR: No se encontró la impresora ***")
        else:
            print(f"\nError USB no manejado: {str(e)}")
        return None
    except Exception as e:
        print(f"\nError general al configurar la impresora: {str(e)}")
        return None

def print_debug(printer):
    """Imprime solo el título en modo debug"""
    printer.set(align='center')
    printer.text("*** TU BOTÓN ***\n")
    printer.text("\n" * 3)
    return True

def print_image(printer, image_path):
    """Procesa e imprime una imagen en la impresora térmica."""
    try:
        print(f"Procesando imagen: {image_path}")
        img = Image.open(image_path)

        # Convertir a escala de grises (L)
        img = img.convert('L')

        # Ajustar tamaño
        max_width = 384
        width, height = img.size
        print(f"Tamaño original de la imagen: {width}x{height}")
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"Imagen redimensionada a: {max_width}x{new_height}")
        else:
            print("La imagen no necesita redimensionarse.")

        # Aumentar contraste significativamente
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)  # Aumentado de 1.5 a 2.5

        # Ajustar brillo para hacer la imagen más oscura
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.8)  # Valor < 1 hace la imagen más oscura

        # Convertir a binario con un umbral más bajo para obtener más píxeles negros
        threshold = 150  # Reducido de 180 a 150
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

        # Invertir el resultado
        img = ImageOps.invert(img)

        # Imprimir la imagen
        printer.set(align='center')
        printer.image(img, impl="bitImageColumn")
        printer.text("\n")
        print("Imagen procesada e impresa con éxito")
        return True

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de imagen en '{image_path}'")
        return False
    except Exception as e:
        print(f"Error detallado al procesar/imprimir la imagen: {str(e)}")
        return False

def get_random_image():
    """Selecciona una imagen aleatoria del directorio images."""
    try:
        # Obtener todas las imágenes que coincidan con el patrón
        image_pattern = os.path.join("images", "imagen_*.png")
        images = glob.glob(image_pattern)
        
        if not images:
            print("No se encontraron imágenes en el directorio images")
            return None
            
        # Seleccionar una imagen aleatoria
        random_image = random.choice(images)
        print(f"Imagen seleccionada: {random_image}")
        return random_image
    except Exception as e:
        print(f"Error al seleccionar imagen aleatoria: {e}")
        return None

def print_art_ticket(printer, estilo_base=None):
    """Imprime el ticket completo con el diseño artístico."""
    try:
        print("\n--- Iniciando impresión del ticket artístico ---")
        
        # 1. Resetear y configurar inicio
        printer.set(align='center')
        
        # En modo debug solo imprimimos el título
        if DEBUG_MODE:
            printer.text("*** TU BOTÓN ***\n")
            printer.text("\n" * 3)  # Avance de papel
            return True

        # Seleccionar estilo aleatorio si no se especifica uno
        if estilo_base is None:
            estilo_base, estilo_info = get_random_style()
        else:
            estilo_info = BUTTON_STYLES.get(estilo_base, {
                "desc": "undefined style",
                "ref": "mixed reference",
                "style_text": "custom style",
                "prompt": "Use undefined style with custom parameters"
            })

        # 2. Encabezado
        printer.text("*** TU BOTÓN ***\n")
        printer.text("--------------------\n")
        printer.text("Instancia Generativa Única\n\n")

        # 3. Imprimir la imagen
        imagen_generada = get_random_image()
        if imagen_generada:
            if not print_image(printer, imagen_generada):
                printer.set(align='center')
                printer.text("[------------------------]\n")
                printer.text("[     (Aquí iría la      ]\n")
                printer.text("[   imagen del botón     ]\n")
                printer.text("[    generado, ~50mm)    ]\n")
                printer.text("[------------------------]\n\n")
        else:
            printer.set(align='center')
            printer.text("[------------------------]\n")
            printer.text("[     (Aquí iría la      ]\n")
            printer.text("[   imagen del botón     ]\n")
            printer.text("[    generado, ~50mm)    ]\n")
            printer.text("[------------------------]\n\n")

        # 4. Información del Diseño
        printer.text("*** DISEÑO ***\n\n")

        # Generar UUID corto para la instancia
        id_instancia = str(uuid.uuid4())[:8]

        printer.set(align='left')
        printer.text(f"ID_Instancia.: {id_instancia}\n")
        printer.text(f"Sistema Base.: {estilo_base}\n")
        
        printer.text("\n--- Atributos ---\n")
        printer.text(f"Estética.....: {estilo_info['desc']}\n")
        printer.text(f"Referencia...: {estilo_info['ref']}\n")
        printer.text(f"Estilo.......: {estilo_info['style_text']}\n")
        printer.text(f"Mediación....: Maquínica\n")
        printer.text(f"Materialidad.: Tinta/Papel APLI 13323\n\n")

        # 5. Sección Reflexión
        printer.text("*** ANÁLISIS ***\n\n")
        printer.text("Necesidad...: No detectada\n")
        printer.text("Exceso.....: Confirmado\n")
        printer.text("Proceso....: Algorítmico\n")
        printer.text("Resultado...: No estándar\n\n")

        # 6. Prompt del estilo
        printer.set(align='center')
        printer.text("*** PROMPT ***\n\n")
        printer.text(f"{estilo_info['prompt']}\n\n")

        # 7. Pie de página
        printer.text("--------------------\n")
        printer.text("Fin de Transmisión\n")

        # Fecha y hora
        now = datetime.datetime.now()
        fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")
        printer.text(f"{fecha_hora}\n")

        # Avance de papel
        printer.text("\n" * 3)

        print("--- Impresión del ticket finalizada ---")
        return True

    except Exception as e:
        print(f"Error durante la impresión del ticket: {str(e)}")
        return False

def draw_image(image_path):
    try:
        # Cargar la imagen
        img = Image.open(image_path)
        
        # Convertir a escala de grises
        img = img.convert('L')
        
        # Ajustar tamaño para que quepa en la pantalla
        max_size = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.8  # 80% del tamaño de la pantalla
        width, height = img.size
        ratio = max_size / max(width, height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convertir a formato Pygame
        img = img.convert('RGB')
        img_surface = pygame.image.fromstring(img.tobytes(), img.size, 'RGB')
        
        # Calcular posición centrada
        x = (SCREEN_WIDTH - new_width) // 2
        y = (SCREEN_HEIGHT - new_height) // 2
        
        # Dibujar la imagen
        screen.blit(img_surface, (x, y))
        return True
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")
        return False

def move_servo_sequence(servo, start_angle, end_angle, steps=5, delay=0.05):
    """Realiza una secuencia de movimientos complejos con el servo"""
    try:
        # Movimiento inicial suave
        move_servo_smoothly(servo, end_angle, steps, delay)
        sleep(0.2)
        
        # Movimiento rápido de regreso
        move_servo_smoothly(servo, start_angle, 3, 0.02)
        sleep(0.1)
        
        # Movimiento intermedio
        move_servo_smoothly(servo, (start_angle + end_angle) / 2, 2, 0.03)
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

def main():
    try:
        # Configurar servo y botón
        servo = setup_servo(SERVO_PIN)
        servo2 = setup_servo(SERVO2_PIN)
        button = Button(BUTTON_PIN)
        print("Servo y pulsador configurados correctamente")
        
        # Configurar impresora solo si SOLO_BOTON es False
        printer = None
        if not SOLO_BOTON:
            printer = setup_printer()
            if not printer:
                print("No se pudo configurar la impresora. Continuando solo con los servos...")
        else:
            print("Modo SOLO_BOTON activado: la impresora está deshabilitada.")
        
        # Posiciones del servo
        neutral_position = -90
        turn_position = 90
        turn_position2 = 90
        neutral_position2 = 30  # Cambiado de 0 a 30 grados
        
        # Iniciar en posición neutral
        #move_servo_smoothly(servo, neutral_position)
        move_servo_smoothly(servo2, neutral_position2)
        #detach_servo(servo)
        detach_servo(servo2)
        
        # Configurar Pygame
        clock = pygame.time.Clock()
        button_visible = False
        current_image = None
        hide_time = None
        
        # Variables para el temporizador
        servo_timer = None
        servo_state = "neutral"  # neutral, waiting, turning, returning
        
        while True:
            # Manejar eventos de Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            current_time = time.time()
            
            # Verificar si el botón físico está presionado
            if button.is_pressed:
                if not button_visible:  # Solo seleccionar nueva imagen si no estaba visible
                    # 1. Seleccionar y mostrar la imagen
                    current_image = get_random_image()
                    button_visible = True
                    hide_time = None
                    print("Pulsador presionado - Mostrando imagen")
                    
                    # 2. Imprimir el ticket
                    if printer:
                        print("Imprimiendo ticket...")
                        if DEBUG_MODE:
                            print_debug(printer)
                        else:
                            print_art_ticket(printer)
                    
                    # --- MODO SOLO_BOTON ---
                    if SOLO_BOTON:
                        # Mover el primer servo normalmente
                        move_servo_smoothly(servo, turn_position)
                        # Realizar la secuencia compleja con el segundo servo
                        move_servo_smoothly(servo2, neutral_position2, turn_position2)
                        sleep(1)  # Breve pausa para mantener el giro
                        move_servo_smoothly(servo, neutral_position)
                        move_servo_smoothly(servo2, neutral_position2)  # Volver a la posición inicial de 30 grados
                        detach_servo(servo)
                        detach_servo(servo2)
                        # Ocultar la imagen después de 2 segundos
                        hide_time = current_time + 2
                        servo_timer = None
                        servo_state = "neutral"
                    else:
                        # 3. Iniciar temporizador para el servo
                        servo_timer = current_time
                        servo_state = "waiting"
                        print("Iniciando temporizador para servo...")
            
            # Manejar estados del servo SOLO si NO es SOLO_BOTON
            if not SOLO_BOTON and servo_timer is not None:
                print(servo_state)
                if servo_state == "waiting" and current_time - servo_timer >= 4:
                    # Mover ambos servos a posición de giro
                    move_servo_smoothly(servo, turn_position)
                    move_servo_smoothly(servo2, turn_position)
                    servo_state = "turning"
                    servo_timer = current_time
                elif servo_state == "turning" and current_time - servo_timer >= 2:
                    # Volver ambos servos a posición neutral
                    move_servo_smoothly(servo, neutral_position)
                    move_servo_smoothly(servo2, neutral_position)
                    detach_servo(servo)
                    detach_servo(servo2)
                    servo_state = "returning"
                    servo_timer = current_time
                elif servo_state == "returning" and current_time - servo_timer >= 0.5:
                    # Establecer el tiempo para ocultar la imagen (5 segundos después)
                    hide_time = current_time + 5
                    servo_timer = None
                    servo_state = "neutral"
            
            # Verificar si es hora de ocultar la imagen
            if hide_time and current_time >= hide_time:
                button_visible = False
                current_image = None
                hide_time = None
            
            # Limpiar la pantalla con fondo blanco
            screen.fill(WHITE)
            
            # Dibujar la imagen solo si es visible
            if button_visible and current_image:
                draw_image(current_image)
            
            # Actualizar la pantalla
            pygame.display.flip()
            clock.tick(60)

    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario")
        if 'servo' in locals():
            detach_servo(servo)
        if 'servo2' in locals():
            detach_servo(servo2)
        if 'printer' in locals():
            printer.close()
        pygame.quit()
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        pygame.quit()

if __name__ == "__main__":
    main() 