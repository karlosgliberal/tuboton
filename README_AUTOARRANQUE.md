# 🚀 Tu Botón - Sistema de Autoarranque

Este documento explica cómo configurar **Tu Botón** para que se inicie automáticamente al arrancar la Raspberry Pi.

## 📋 Resumen del Sistema

La solución implementada usa **systemd** + **script de control** para proporcionar:

- ✅ **Reinicio automático** si la aplicación falla
- ✅ **Control total** (start/stop/restart/status)
- ✅ **Logs centralizados** con journalctl
- ✅ **Verificaciones de dependencias**
- ✅ **Manejo robusto de errores**
- ✅ **Fácil acceso por SSH**

## 🛠️ Instalación Rápida

```bash
# 1. Instalar el sistema de autoarranque
./install_autostart.sh

# 2. Verificar la instalación
./tuboton.sh check

# 3. Iniciar el servicio (si no se reinició)
./tuboton.sh start
```

## 🎛️ Comandos Disponibles

### Script de Control (`./tuboton.sh`)

```bash
# Operaciones básicas
./tuboton.sh start          # Iniciar el servicio
./tuboton.sh stop           # Detener el servicio  
./tuboton.sh restart        # Reiniciar el servicio
./tuboton.sh status         # Ver estado del servicio

# Monitoreo
./tuboton.sh logs           # Ver logs en tiempo real
./tuboton.sh logs-full      # Ver todos los logs
./tuboton.sh check          # Verificar dependencias

# Gestión del servicio
./tuboton.sh enable         # Habilitar autoarranque
./tuboton.sh disable        # Deshabilitar autoarranque
./tuboton.sh install        # Instalar servicio manualmente
./tuboton.sh uninstall      # Desinstalar servicio

# Testing
./tuboton.sh test           # Ejecutar sin servicio (modo desarrollo)
```

### Comandos systemd Directos

```bash
# Estado del servicio
sudo systemctl status tuboton

# Logs del servicio
journalctl -f -u tuboton           # Tiempo real
journalctl -u tuboton --since today   # Desde hoy
journalctl -u tuboton -n 50        # Últimas 50 líneas

# Control manual
sudo systemctl start tuboton
sudo systemctl stop tuboton
sudo systemctl restart tuboton
```

## 📁 Archivos del Sistema

```
/home/wintermute/tuboton/
├── main.py                    # Aplicación principal (mejorada)
├── config.py                  # Configuración
├── tuboton.service           # Archivo de servicio systemd
├── tuboton.sh                # Script de control
├── install_autostart.sh      # Instalador automático
└── README_AUTOARRANQUE.md    # Esta documentación

/etc/systemd/system/
└── tuboton.service           # Servicio instalado

/var/log/
└── tuboton.log              # Logs de la aplicación
```

## 🔧 Características Técnicas

### Servicio systemd (`tuboton.service`)

- **Reinicio automático**: Si falla, se reinicia en 10 segundos
- **Límite de reintentos**: Máximo 3 intentos en 60 segundos
- **Dependencias**: Espera a `multi-user.target` y `network.target`
- **Usuario**: Ejecuta como `wintermute` (no root)
- **Permisos**: Acceso a GPIO, USB, video y audio
- **Variables de entorno**: DISPLAY, XAUTHORITY configurados
- **Recursos**: Límite de 512MB RAM y 80% CPU

### Mejoras en main.py

- **Logging robusto**: Logs a archivo y consola
- **Verificación de entorno**: Chequea dependencias al iniciar
- **Manejo de señales**: Limpieza ordenada con SIGTERM/SIGINT
- **Cleanup automático**: Libera recursos al salir
- **Delays de inicialización**: Para hardware y X11
- **Variables globales**: Para limpieza desde signal handlers

## 🚨 Solución de Problemas

### 1. El servicio no inicia

```bash
# Ver el estado detallado
./tuboton.sh status

# Ver logs de error
./tuboton.sh logs-full

# Verificar dependencias
./tuboton.sh check

# Probar en modo desarrollo
./tuboton.sh test
```

### 2. Problemas de permisos

```bash
# Verificar grupos del usuario
groups wintermute

# Añadir permisos manualmente
sudo usermod -a -G gpio,dialout,video,audio wintermute

# Reiniciar para aplicar permisos
sudo reboot
```

### 3. Error de display/X11

```bash
# Verificar DISPLAY
echo $DISPLAY

# Verificar que X11 está corriendo
ps aux | grep X

# En algunas configuraciones puede necesitar:
export DISPLAY=:0.0
```

### 4. Impresora no detectada

```bash
# Verificar conexión USB
lsusb | grep -i printer

# Verificar permisos USB
ls -la /dev/bus/usb/*/

# Reiniciar servicio después de conectar impresora
./tuboton.sh restart
```

### 5. Servos no responden

```bash
# Verificar permisos GPIO
groups $USER | grep gpio

# Verificar que no hay conflictos GPIO
sudo gpio readall

# Verificar configuración de pines en config.py
```

## 📊 Monitoreo

### Ver logs en tiempo real
```bash
./tuboton.sh logs
# o
journalctl -f -u tuboton
```

### Verificar uso de recursos
```bash
# CPU y memoria del servicio
systemctl status tuboton

# Procesos relacionados
ps aux | grep python | grep main.py
```

### Estado del autoarranque
```bash
systemctl is-enabled tuboton
systemctl is-active tuboton
```

## 🔄 Reinicio y Recuperación

### Reinicio normal
- El sistema se reinicia automáticamente si falla
- Límite: 3 intentos en 60 segundos
- Delay: 10 segundos entre reintentos

### Reinicio manual
```bash
./tuboton.sh restart
```

### Recuperación total
```bash
# Detener servicio
./tuboton.sh stop

# Verificar que no quedan procesos
ps aux | grep main.py

# Limpiar logs si es necesario
sudo truncate -s 0 /var/log/tuboton.log

# Reiniciar
./tuboton.sh start
```

## 🛠️ Desinstalación

```bash
# Desinstalar completamente
./tuboton.sh uninstall

# Verificar que se eliminó
systemctl status tuboton
```

## 📝 Logs Importantes

### Ubicaciones de logs
- **Aplicación**: `/var/log/tuboton.log`
- **Systemd**: `journalctl -u tuboton`
- **Sistema**: `/var/log/syslog`

### Filtros útiles
```bash
# Solo errores
journalctl -u tuboton -p err

# Desde el último arranque
journalctl -u tuboton -b

# Últimas 2 horas
journalctl -u tuboton --since "2 hours ago"
```

## ⚡ Comandos Rápidos de Emergencia

```bash
# Parar TODO inmediatamente
sudo systemctl stop tuboton
sudo pkill -f main.py

# Ver QUÉ está pasando
./tuboton.sh status
./tuboton.sh logs | tail -20

# Reiniciar limpio
./tuboton.sh restart

# Verificar DEPENDENCIAS
./tuboton.sh check
```

---

## 🎯 Ventajas de esta Solución

1. **Sin bloqueo del sistema**: Si Tu Botón falla, no afecta el arranque
2. **Control total**: Puedes parar/iniciar cuando quieras
3. **Logs completos**: Sabes exactamente qué está pasando
4. **Reinicio inteligente**: No reinicia infinitamente si hay errores permanentes
5. **Fácil acceso SSH**: Puedes controlarlo remotamente
6. **Modo desarrollo**: Puedes probar cambios sin afectar el servicio

¡El sistema está diseñado para ser robusto y fácil de manejar! 🚀 