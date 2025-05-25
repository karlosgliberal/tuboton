#!/bin/bash

# Script de control para Tu Botón
# Facilita el manejo del servicio systemd

SERVICE_NAME="tuboton"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR="/home/wintermute/tuboton"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar estado con colores
show_status() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "Estado: ${GREEN}ACTIVO${NC}"
    else
        echo -e "Estado: ${RED}INACTIVO${NC}"
    fi
    
    if systemctl is-enabled --quiet $SERVICE_NAME; then
        echo -e "Autoarranque: ${GREEN}HABILITADO${NC}"
    else
        echo -e "Autoarranque: ${YELLOW}DESHABILITADO${NC}"
    fi
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}=== CONTROL DE TU BOTÓN ===${NC}"
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start       - Iniciar el servicio"
    echo "  stop        - Detener el servicio"
    echo "  restart     - Reiniciar el servicio"
    echo "  status      - Mostrar estado del servicio"
    echo "  enable      - Habilitar autoarranque"
    echo "  disable     - Deshabilitar autoarranque"
    echo "  logs        - Mostrar logs en tiempo real"
    echo "  logs-full   - Mostrar todos los logs"
    echo "  install     - Instalar el servicio"
    echo "  uninstall   - Desinstalar el servicio"
    echo "  test        - Ejecutar en modo test (sin servicio)"
    echo "  check       - Verificar dependencias"
    echo ""
    show_status
}

# Verificar dependencias
check_dependencies() {
    echo -e "${BLUE}Verificando dependencias...${NC}"
    
    # Python y módulos
    echo -n "Python3: "
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    # Módulos de Python
    modules=("pygame" "gpiozero" "escpos" "PIL" "qrcode" "usb")
    for module in "${modules[@]}"; do
        echo -n "$module: "
        if python3 -c "import $module" &> /dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    done
    
    # Permisos de GPIO
    echo -n "Permisos GPIO: "
    if groups $USER | grep -q gpio; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}?${NC} (ejecuta: sudo usermod -a -G gpio $USER)"
    fi
    
    # Display
    echo -n "Display X11: "
    if [ ! -z "$DISPLAY" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}?${NC} (no hay DISPLAY configurado)"
    fi
    
    # Archivos del proyecto
    echo -n "main.py: "
    if [ -f "$PROJECT_DIR/main.py" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "config.py: "
    if [ -f "$PROJECT_DIR/config.py" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo -n "Directorio images/: "
    if [ -d "$PROJECT_DIR/images" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
}

# Función principal
case "$1" in
    start)
        echo -e "${BLUE}Iniciando Tu Botón...${NC}"
        sudo systemctl start $SERVICE_NAME
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Servicio iniciado${NC}"
        else
            echo -e "${RED}✗ Error al iniciar servicio${NC}"
        fi
        ;;
    
    stop)
        echo -e "${BLUE}Deteniendo Tu Botón...${NC}"
        sudo systemctl stop $SERVICE_NAME
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Servicio detenido${NC}"
        else
            echo -e "${RED}✗ Error al detener servicio${NC}"
        fi
        ;;
    
    restart)
        echo -e "${BLUE}Reiniciando Tu Botón...${NC}"
        sudo systemctl restart $SERVICE_NAME
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Servicio reiniciado${NC}"
        else
            echo -e "${RED}✗ Error al reiniciar servicio${NC}"
        fi
        ;;
    
    status)
        echo -e "${BLUE}=== ESTADO DE TU BOTÓN ===${NC}"
        show_status
        echo ""
        systemctl status $SERVICE_NAME --no-pager
        ;;
    
    enable)
        echo -e "${BLUE}Habilitando autoarranque...${NC}"
        sudo systemctl enable $SERVICE_NAME
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Autoarranque habilitado${NC}"
        else
            echo -e "${RED}✗ Error al habilitar autoarranque${NC}"
        fi
        ;;
    
    disable)
        echo -e "${BLUE}Deshabilitando autoarranque...${NC}"
        sudo systemctl disable $SERVICE_NAME
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Autoarranque deshabilitado${NC}"
        else
            echo -e "${RED}✗ Error al deshabilitar autoarranque${NC}"
        fi
        ;;
    
    logs)
        echo -e "${BLUE}Logs en tiempo real (Ctrl+C para salir):${NC}"
        journalctl -f -u $SERVICE_NAME
        ;;
    
    logs-full)
        echo -e "${BLUE}Todos los logs:${NC}"
        journalctl -u $SERVICE_NAME --no-pager
        ;;
    
    install)
        echo -e "${BLUE}Instalando servicio Tu Botón...${NC}"
        
        # Verificar que existe el archivo de servicio
        if [ ! -f "$PROJECT_DIR/tuboton.service" ]; then
            echo -e "${RED}✗ No se encontró tuboton.service en $PROJECT_DIR${NC}"
            exit 1
        fi
        
        # Copiar archivo de servicio
        sudo cp "$PROJECT_DIR/tuboton.service" "$SERVICE_FILE"
        
        # Recargar systemd
        sudo systemctl daemon-reload
        
        # Habilitar autoarranque
        sudo systemctl enable $SERVICE_NAME
        
        echo -e "${GREEN}✓ Servicio instalado y habilitado${NC}"
        echo -e "${YELLOW}Usa './tuboton.sh start' para iniciarlo${NC}"
        ;;
    
    uninstall)
        echo -e "${BLUE}Desinstalando servicio Tu Botón...${NC}"
        
        # Detener y deshabilitar
        sudo systemctl stop $SERVICE_NAME 2>/dev/null
        sudo systemctl disable $SERVICE_NAME 2>/dev/null
        
        # Eliminar archivo de servicio
        sudo rm -f "$SERVICE_FILE"
        
        # Recargar systemd
        sudo systemctl daemon-reload
        
        echo -e "${GREEN}✓ Servicio desinstalado${NC}"
        ;;
    
    test)
        echo -e "${BLUE}Ejecutando en modo test...${NC}"
        cd "$PROJECT_DIR"
        python3 main.py
        ;;
    
    check)
        check_dependencies
        ;;
    
    *)
        show_help
        ;;
esac 