#!/usr/bin/env python3

import pygame
from PIL import Image
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

class DisplayController:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Tu Botón")
        self.clock = pygame.time.Clock()
        self.current_image = None
        self.button_visible = False
        self.hide_time = None

    def draw_image(self, image_path):
        """Dibuja una imagen en la pantalla"""
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
            self.screen.blit(img_surface, (x, y))
            return True
        except Exception as e:
            print(f"Error al mostrar la imagen: {str(e)}")
            return False

    def handle_events(self):
        """Maneja los eventos de Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def update_display(self):
        """Actualiza la pantalla"""
        # Limpiar la pantalla con fondo blanco
        self.screen.fill(WHITE)
        
        # Dibujar la imagen si es visible
        if self.button_visible and self.current_image:
            self.draw_image(self.current_image)
        
        # Actualizar la pantalla
        pygame.display.flip()
        self.clock.tick(60)

    def show_image(self, image_path):
        """Muestra una imagen en la pantalla"""
        self.current_image = image_path
        self.button_visible = True
        self.hide_time = None

    def hide_image(self):
        """Oculta la imagen actual"""
        self.button_visible = False
        self.current_image = None
        self.hide_time = None

    def set_hide_time(self, time):
        """Establece el tiempo para ocultar la imagen"""
        self.hide_time = time

    def should_hide_image(self, current_time):
        """Verifica si es hora de ocultar la imagen"""
        if self.hide_time and current_time >= self.hide_time:
            self.hide_image()
            return True
        return False

    def cleanup(self):
        """Limpia los recursos de Pygame"""
        pygame.quit() 