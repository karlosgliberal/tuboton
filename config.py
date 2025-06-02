#!/usr/bin/env python3

# --- Configuración de la Impresora ---
VENDOR_ID = 0x0416
PRODUCT_ID = 0x5011

# --- Configuración de Debug ---
DEBUG_MODE = False   # Cambia a False para modo normal

# --- Configuración Solo Botón ---
SOLO_BOTON = False # Si es True, la impresora no se inicializa ni se usa

# --- Configuración del Servo ---
SERVO_PIN = 18
BUTTON_PIN = 17
SERVO2_PIN = 21  # Nuevo pin para el segundo servo

# --- Configuración de Pygame ---
import pygame
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

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

# Estilos de botones
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

# --- Configuración del QR ---
QR_URL = "http://tuboton.karlosgliberal.com/"  # Cambiar por la URL real
QR_SIZE = 3  # Tamaño del QR (1-10, donde 3 es tamaño mediano)
QR_BORDER = 2  # Borde alrededor del QR en píxeles

# --- Sistema de Probabilidad ---
# Probabilidades para las acciones del botón (deben sumar 100)
PROB_SOLO_IMAGEN = 60      # Solo mostrar imagen en pantalla
PROB_TICKET_QR = 30        # Imprimir solo ticket QR  
PROB_TICKET_SERVOS = 10     # Imprimir ticket largo + activar servos

# Verificación automática (no modificar)
_TOTAL_PROB = PROB_SOLO_IMAGEN + PROB_TICKET_QR + PROB_TICKET_SERVOS
if _TOTAL_PROB != 100:
    print(f"⚠️ ADVERTENCIA: Las probabilidades suman {_TOTAL_PROB}% en lugar de 100%")
    print(f"   SOLO_IMAGEN: {PROB_SOLO_IMAGEN}%")
    print(f"   TICKET_QR: {PROB_TICKET_QR}%") 
    print(f"   TICKET_SERVOS: {PROB_TICKET_SERVOS}%") 