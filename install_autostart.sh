#!/bin/bash

# Script de instalación para Tu Botón - Autoarranque
# Este script configura el autoarranque del servicio systemd

PROJECT_DIR="/home/wintermute/tuboton"
SERVICE_NAME="tuboton"
USER_NAME="wintermute"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  INSTALADOR DE AUTOARRANQUE${NC}"
echo -e "${BLUE}         TU BOTÓN${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Verificar que se ejecuta como root
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}❌ No ejecutes este script como root${NC}"
    echo -e "${YELLOW}Ejecuta: ./install_autostart.sh${NC}"
    exit 1
fi

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ] || [ ! -f "config.py" ]; then
    echo -e "${RED}❌ No se encontraron los archivos del proyecto${NC}"
    echo -e "${YELLOW}Asegúrate de ejecutar este script desde el directorio del proyecto${NC}"
    exit 1
fi

echo -e "${BLUE}🔍 Verificando dependencias...${NC}"

# Verificar que tuboton.service existe
if [ ! -f "tuboton.service" ]; then
    echo -e "${RED}❌ No se encontró tuboton.service${NC}"
    exit 1
fi

# Verificar que tuboton.sh existe y es ejecutable
if [ ! -f "tuboton.sh" ]; then
    echo -e "${RED}❌ No se encontró tuboton.sh${NC}"
    exit 1
fi

if [ ! -x "tuboton.sh" ]; then
    echo -e "${YELLOW}⚠️  Haciendo tuboton.sh ejecutable...${NC}"
    chmod +x tuboton.sh
fi

echo -e "${GREEN}✓ Archivos del proyecto verificados${NC}"

# Verificar permisos de usuario
echo -e "${BLUE}🔍 Verificando permisos de usuario...${NC}"

if ! groups $USER | grep -q gpio; then
    echo -e "${YELLOW}⚠️  Añadiendo usuario al grupo GPIO...${NC}"
    sudo usermod -a -G gpio $USER
    echo -e "${GREEN}✓ Usuario añadido al grupo GPIO${NC}"
    REBOOT_NEEDED=true
else
    echo -e "${GREEN}✓ Usuario ya tiene permisos GPIO${NC}"
fi

if ! groups $USER | grep -q dialout; then
    echo -e "${YELLOW}⚠️  Añadiendo usuario al grupo dialout...${NC}"
    sudo usermod -a -G dialout $USER
    echo -e "${GREEN}✓ Usuario añadido al grupo dialout${NC}"
    REBOOT_NEEDED=true
else
    echo -e "${GREEN}✓ Usuario ya tiene permisos dialout${NC}"
fi

# Crear directorio de logs si no existe
echo -e "${BLUE}📁 Configurando directorios de logs...${NC}"
if [ ! -f "/var/log/tuboton.log" ]; then
    sudo touch /var/log/tuboton.log
    sudo chown $USER:$USER /var/log/tuboton.log
    echo -e "${GREEN}✓ Archivo de log creado${NC}"
else
    echo -e "${GREEN}✓ Archivo de log ya existe${NC}"
fi

# Instalar el servicio
echo -e "${BLUE}⚙️  Instalando servicio systemd...${NC}"

# Copiar archivo de servicio
sudo cp tuboton.service /etc/systemd/system/

# Verificar que se copió correctamente
if [ ! -f "/etc/systemd/system/tuboton.service" ]; then
    echo -e "${RED}❌ Error al copiar el archivo de servicio${NC}"
    exit 1
fi

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar autoarranque
sudo systemctl enable tuboton

# Verificar que se habilitó
if systemctl is-enabled --quiet tuboton; then
    echo -e "${GREEN}✓ Servicio instalado y habilitado para autoarranque${NC}"
else
    echo -e "${RED}❌ Error al habilitar el servicio${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 INSTALACIÓN COMPLETADA${NC}"
echo ""
echo -e "${BLUE}=== COMANDOS DISPONIBLES ===${NC}"
echo -e "${YELLOW}./tuboton.sh start${NC}      - Iniciar el servicio"
echo -e "${YELLOW}./tuboton.sh stop${NC}       - Detener el servicio"
echo -e "${YELLOW}./tuboton.sh restart${NC}    - Reiniciar el servicio"
echo -e "${YELLOW}./tuboton.sh status${NC}     - Ver estado del servicio"
echo -e "${YELLOW}./tuboton.sh logs${NC}       - Ver logs en tiempo real"
echo -e "${YELLOW}./tuboton.sh check${NC}      - Verificar dependencias"
echo ""

if [ "$REBOOT_NEEDED" = true ]; then
    echo -e "${YELLOW}⚠️  IMPORTANTE: Es necesario reiniciar para aplicar los permisos de grupo${NC}"
    echo -e "${YELLOW}   Después del reinicio, Tu Botón se iniciará automáticamente${NC}"
    echo ""
    echo -e "${BLUE}¿Quieres reiniciar ahora? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Reiniciando sistema...${NC}"
        sudo reboot
    else
        echo -e "${YELLOW}Recuerda reiniciar manualmente más tarde${NC}"
    fi
else
    echo -e "${BLUE}¿Quieres iniciar Tu Botón ahora? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Iniciando Tu Botón...${NC}"
        ./tuboton.sh start
    else
        echo -e "${YELLOW}Puedes iniciarlo más tarde con: ./tuboton.sh start${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Tu Botón se iniciará automáticamente en cada arranque del sistema${NC}"
echo -e "${BLUE}======================================${NC}" 