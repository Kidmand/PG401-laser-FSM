# Aplicación PyQt6 a Desarrollar

## Objetivo

Desarrollar una aplicación de escritorio en Python + PyQt6, destinada a operar el sistema LazServ mediante comandos HTTP REST. La interfaz debe permitir a operadores científicos manejar y monitorear el sistema tal como permite la API REST más fácilmente.

```md
┌───────────────────┐   HTTP GET    ┌──────────────────┐
│   PyQt6 App       │ ────────────► │ LazServ:8081     │
│   (A HACER)       │               │ (EXISTE 100%)    │
│ [IP: ________]    │ ◄──────────── │                  │
│ [FIRE] [STOP]     │ HTML Response │ - FSM Engine     │
│ [INIT]            │               │ - REST API       │
│ Estado: INIT      │               │ - SQLite DBs     │
│ Respuesta: <HTML> │               │ - Todo funciona  │
└───────────────────┘               └──────────────────┘
```

## Requisitos No Funcionales

### Tecnología y Arquitectura

- **Python 3.13.5** con `PyQt6` para interfaz gráfica
- **Graficos** con `pyqtgraph` para visualización de datos
- **Archivo ejecutable** (.exe) para Windows usando `PyInstaller`
- **Cliente HTTP** con `requests` library para comunicación REST
- **Manejo asíncrono** con `QTimer` para actualizaciones periódicas
- **Configuración persistente** en archivo `JSON` local

### Performance y Comunicación

- **Timeout HTTP**: 5 segundos por request
- **Actualización automática** cada 2 segundos para variables del sistema
- **Actualización de sensores**: cada 200ms (5x más rápido que retención de datos)
- **Buffer local** de 1000 registros por canal de sensores
- **Auto-reconexión** cada 5 segundos en caso de pérdida

### Robustez y Manejo de Errores

- **Validación de entrada**: IP válida, puerto numérico
- **Manejo de excepciones** HTTP (timeout, conexión, protocolo)
- **Estados de error diferenciados**: Red, Protocolo, FSM, Hardware
- **Log de eventos** con timestamp y niveles (Info, Warning, Error)
- **Recuperación automática** de conexión con notificación visual

## Requisitos Funcionales

### 1. Gestión de Conexión

**Configuración de servidor:**

- Campo IP editable con validación (formato IPv4)
- Campo puerto (default: 8081) con validación numérica
- ComboBox con últimas 5 conexiones exitosas (persistente)

**Estado de conexión:**

- Timestamp último ping exitoso con latencia en ms
- Estado del servidor LazServ (Online/Offline/Error)
- Información del sistema: ProductID, ProductSN, versión firmware

**Validación POST-conexión:**

- Test REST: `GET /?RDVAR/State` (debe retornar estado FSM válido)
- Test BD: `GET /?LIST/MSG` (verificar acceso SQLite unilaz.db)
- Test FSM: verificar estado != Fault al conectar

### 2. Control de Estado FSM

**Comandos:**

- [FIRE]: `GET /?EXE/Fire` - Iniciar secuencia láser
- [STOP]: `GET /?EXE/Stop` - Detener operación actual
- [INIT]: `GET /?EXE/Init` - Inicializar sistema completo

**Información de estado:**

- Estado FSM actual: Idle, Busy, Error, Fault (color-coded)
- Última respuesta del servidor (raw HTML en área de texto)
- Ticket del último comando ejecutado
- Habilitación condicional de botones según estado FSM

### 3. Ejecución de Comandos Personalizados

**Interface de comandos:**

- ComboBox poblado desde `/?LIST/SEQUENCES/DISTINCT SEQUENCE`
- Campo parámetro opcional (texto libre)
- Botón [Ejecutar]: envía `/?EXE/{comando}/{parámetro}`
- Display del ticket asignado con botón [Verificar Estado]

**Seguimiento de ejecución:**

- Link clickeable a `/?CES/{ticket}` para verificación
- Historia de últimos 10 comandos ejecutados
- Estado de cada comando: Pending, Running, Success, Error

### 4. Monitoreo de Variables del Sistema

**Variables core (auto-refresh cada 2s):**

- State: `/?RDVAR/State`
- LogBlab: `/?RDVAR/LogBlab`
- x: `/?RDVAR/x`
- ProductID: `/?RDVAR/ProductID`
- ProductSN: `/?RDVAR/ProductSN`

**Interface:**

- Tabla: Variable | Valor
- Botón [Refrescar Manual] para actualización inmediata
- Indicador visual de última actualización exitosa

### 5. Visualización de Log de Ejecución

**Fuente de datos:**

- Query: `/?LIST/CLOG/TIME,STEP,FAULT,RESULT,SRC ORDER BY TIME DESC LIMIT 100`

**Funcionalidades:**

- Tabla: Timestamp | Comando | Estado | Resultado | Fuente

### 6. Datos de Sensores por Canal

**Selección y configuración:**

- SpinBox para número de canal (1-N, extraído de `/?DATA/1` para detectar canales)
- Configuración de frecuencia de actualización (100ms-1000ms) automatica y manual
- Límite de registros a mostrar (últimos 100-1000)

**Visualización de datos:**

- Query inicial: `/?DATA/{canal}`
- Query incremental: `/?DATA/{canal}/{último_timestamp}`
- Tabla: Timestamp | Canal | Valor | unidades
- Gráfico en tiempo real

**Gestión de datos:**

- Buffer local para evitar pérdida de datos
- Indicador de pérdida de datos (gap en timestamps)
- Estadísticas: Min, Max, Promedio, Desviación estándar

### 7. Estado de Comandos (Tickets)

**Interface de consulta:**

- Campo entrada para ticket ID
- Botón [Consultar]: `/?CES/{ticket}`
- Auto-consulta para comandos ejecutados desde la app

**Información mostrada:**

- Código de estado, Paso actual, Resultado
- Fuente del comando, Timestamp de ejecución
- Mensajes de error detallados con códigos
