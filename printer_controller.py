#!/usr/bin/env python3

import usb.core
import usb.util
from escpos.printer import Usb
from PIL import Image, ImageEnhance, ImageOps
import glob
import random
import os
import uuid
import datetime
from config import VENDOR_ID, PRODUCT_ID, DEBUG_MODE, BUTTON_STYLES

class PrinterController:
    def __init__(self):
        self.printer = self._setup_printer()

    def _setup_printer(self):
        try:
            return Usb(VENDOR_ID, PRODUCT_ID, timeout=0, in_ep=0x81, out_ep=0x01)
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

    def print_debug(self):
        """Imprime solo el título en modo debug"""
        if not self.printer:
            return False
        self.printer.set(align='center')
        self.printer.text("*** TU BOTÓN ***\n")
        self.printer.text("\n" * 3)
        return True

    def print_image(self, image_path):
        """Procesa e imprime una imagen en la impresora térmica."""
        if not self.printer:
            return False
            
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
            img = enhancer.enhance(2.5)

            # Ajustar brillo para hacer la imagen más oscura
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.8)

            # Convertir a binario con un umbral más bajo para obtener más píxeles negros
            threshold = 150
            img = img.point(lambda x: 0 if x < threshold else 255, '1')

            # Invertir el resultado
            img = ImageOps.invert(img)

            # Imprimir la imagen
            self.printer.set(align='center')
            self.printer.image(img, impl="bitImageColumn")
            self.printer.text("\n")
            print("Imagen procesada e impresa con éxito")
            return True

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo de imagen en '{image_path}'")
            return False
        except Exception as e:
            print(f"Error detallado al procesar/imprimir la imagen: {str(e)}")
            return False

    def get_random_image(self):
        """Selecciona una imagen aleatoria del directorio images."""
        try:
            image_pattern = os.path.join("images", "imagen_*.png")
            images = glob.glob(image_pattern)
            
            if not images:
                print("No se encontraron imágenes en el directorio images")
                return None
                
            random_image = random.choice(images)
            print(f"Imagen seleccionada: {random_image}")
            return random_image
        except Exception as e:
            print(f"Error al seleccionar imagen aleatoria: {e}")
            return None

    def get_random_style(self):
        """Selecciona un estilo aleatorio del diccionario de estilos."""
        style_name = random.choice(list(BUTTON_STYLES.keys()))
        return style_name, BUTTON_STYLES[style_name]

    def print_art_ticket(self, estilo_base=None):
        """Imprime el ticket completo con el diseño artístico."""
        if not self.printer:
            return False
            
        try:
            print("\n--- Iniciando impresión del ticket artístico ---")
            
            # 1. Resetear y configurar inicio
            self.printer.set(align='center')
            
            # En modo debug solo imprimimos el título
            if DEBUG_MODE:
                self.printer.text("*** TU BOTÓN ***\n")
                self.printer.text("\n" * 3)
                return True

            # Seleccionar estilo aleatorio si no se especifica uno
            if estilo_base is None:
                estilo_base, estilo_info = self.get_random_style()
            else:
                estilo_info = BUTTON_STYLES.get(estilo_base, {
                    "desc": "undefined style",
                    "ref": "mixed reference",
                    "style_text": "custom style",
                    "prompt": "Use undefined style with custom parameters"
                })

            # 2. Encabezado
            self.printer.text("*** TU BOTÓN ***\n")
            self.printer.text("--------------------\n")
            self.printer.text("Instancia Generativa Única\n\n")

            # 3. Imprimir la imagen
            imagen_generada = self.get_random_image()
            if imagen_generada:
                if not self.print_image(imagen_generada):
                    self._print_image_placeholder()
            else:
                self._print_image_placeholder()

            # 4. Información del Diseño
            self.printer.text("*** DISEÑO ***\n\n")

            # Generar UUID corto para la instancia
            id_instancia = str(uuid.uuid4())[:8]

            self.printer.set(align='left')
            self.printer.text(f"ID_Instancia.: {id_instancia}\n")
            self.printer.text(f"Sistema Base.: {estilo_base}\n")
            
            self.printer.text("\n--- Atributos ---\n")
            self.printer.text(f"Estética.....: {estilo_info['desc']}\n")
            self.printer.text(f"Referencia...: {estilo_info['ref']}\n")
            self.printer.text(f"Estilo.......: {estilo_info['style_text']}\n")
            self.printer.text(f"Mediación....: Maquínica\n")
            self.printer.text(f"Materialidad.: Tinta/Papel APLI 13323\n\n")

            # 5. Sección Reflexión
            self.printer.text("*** ANÁLISIS ***\n\n")
            self.printer.text("Necesidad...: No detectada\n")
            self.printer.text("Exceso.....: Confirmado\n")
            self.printer.text("Proceso....: Algorítmico\n")
            self.printer.text("Resultado...: No estándar\n\n")

            # 6. Prompt del estilo
            self.printer.set(align='center')
            self.printer.text("*** PROMPT ***\n\n")
            self.printer.text(f"{estilo_info['prompt']}\n\n")

            # 7. Pie de página
            self.printer.text("--------------------\n")
            self.printer.text("Fin de Transmisión\n")

            # Fecha y hora
            now = datetime.datetime.now()
            fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")
            self.printer.text(f"{fecha_hora}\n")

            # Avance de papel
            self.printer.text("\n" * 3)

            print("--- Impresión del ticket finalizada ---")
            return True

        except Exception as e:
            print(f"Error durante la impresión del ticket: {str(e)}")
            return False

    def _print_image_placeholder(self):
        """Imprime un placeholder cuando no hay imagen disponible"""
        self.printer.set(align='center')
        self.printer.text("[------------------------]\n")
        self.printer.text("[     (Aquí iría la      ]\n")
        self.printer.text("[   imagen del botón     ]\n")
        self.printer.text("[    generado, ~50mm)    ]\n")
        self.printer.text("[------------------------]\n\n")

    def cleanup(self):
        """Limpia los recursos de la impresora"""
        if self.printer:
            self.printer.close() 