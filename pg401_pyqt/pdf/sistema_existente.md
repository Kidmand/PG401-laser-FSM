# Sistema Necesario Existente (LazServ - Placa de Control Linux)

## Descripción General

- **Máquina de Estados Finitos (FSM)** completamente funcional
- Estados FSM Predefinidos
  - **Init** → **Idle** → **Fire** → **Stop** → **Fault**
  - Transiciones automáticas basadas en comandos
  - Manejo de errores integrado con códigos específicos
- **Servidor HTTP REST** operativo en puerto 8081
- **Bases de datos SQLite** configuradas y pobladas:
  - `unilaz.db` - configuración y tablas del sistema
  - `log.db` - logs de sesión automáticos
  - Tablas en memoria: `TLOG`, `DLOG` para datos en tiempo real

## API REST Completamente Funcional

- **URL Base**: `http://xxx.xxx.xxx.xxx:8081/REST/HTTP_CMD/?<action>`
- **action** puede ser:
  - **query**: consulta de estado de ejecución, variables o datos de sensores. La consulta no cambia el estado de la FSM.
  - **command and parameters**: instrucciones para la FSM que alterarán el estado. Los comandos son de una sola palabra y pueden tener parámetros opcionales separados por "/".

### Comandos para Manejo de Errores

| Nombre          | Parámetro                  | Acción                                                                                                                                                                                                       | Uso Típico                                                                                                                 |
| --------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| `ResetErr`      | —                          | El error se borra. Se registra en el log como `'Clean completion'` con código de éxito.                                                                                                                      | Se usa junto con el comando `waitfor` como retardo de tiempo fijo.                                                         |
| `IgnoreErr`     | —                          | El error se borra. Se registra `'Next: Ignore error'` en el log con código de **error**.                                                                                                                     | Útil en depuración para no interrumpir la ejecución, pero dejar rastro del error en el log.                                |
| `SkipRestOnErr` | Opcional: código sustituto | Se registra `'Next: Skipping rest'` en el log con el código de error original o sustituido. La ejecución de la secuencia se **interrumpe**.                                                                  | Se usa al inicio de la secuencia como "guardas". Si no se cumplen, no se ejecutan más pasos y el estado del FSM no cambia. |
| `FaultOnErr`    | Opcional: código sustituto | Se publica el evento `'GoToFault'` en la cola. Se registra `'Next: GoToFault'` en el log con el código de error original o sustituido. La secuencia actual se termina y se ejecuta la secuencia `GoToFault`. | Se usa para redirigir el FSM al modo de falla (fault).                                                                     |

- Los **códigos sustitutos** en `SkipRestOnErr` y `FaultOnErr` permiten reemplazar el mensaje de error estándar por uno **más específico del sistema**.
- Ejemplo: si un bit que representa un interlock de seguridad no tiene el valor esperado, normalmente el FSM dirá algo como "el bit tiene valor `x` en lugar de `y`". Pero con código sustituto, podés mostrar un mensaje más claro y personalizado para facilitar la resolución de problemas.

### Comando `EXE` (Ejecución de Secuencias)

El comando `EXE` permite iniciar la ejecución de una secuencia predefinida en la Máquina de Estados Finitos (FSM) del sistema. Es el mecanismo principal para solicitar acciones automáticas, como iniciar, detener o cambiar el modo de operación del equipo. Cada ejecución genera un "ticket" (timestamp) que sirve para consultar el estado de la orden enviada.

#### Sintaxis

- **Consulta**:

  ```txt
  EXE/<Comando>[/Parámetro]
  ```

  - `<Comando>`: Nombre de la secuencia a ejecutar (por ejemplo, `Stop`, `Fire`, `Init`).
  - `[Parámetro]` (opcional): Valor que se asigna a la variable `x` antes de ejecutar la secuencia, útil para comandos que requieren argumentos.
- **Respuesta**:

  ```html
  %d<br><a href="?CES/%d">Check status</a>
  ```

  - `%d`: `0` si el comando fue aceptado, el código de error si hubo un problema.
  - `%d`: Ticket del comando, que es un timestamp único que identifica la ejecución.

#### Detalles Técnicos

- **Función interna:** `exeSEQM`

#### Ejemplo de Uso

- Ejecutar el comando `Stop`: `http://192.168.0.160:8081/REST/HTTP_CMD/?EXE/Stop`
- Respuesta exitosa:
  
  ```html
  0<br><a href="?CES/3575601570403">Check status</a>
  ```

#### Flujo de Ejecución

1. El comando se envía mediante una solicitud HTTP GET.
2. El FSM coloca la orden en su cola interna de ejecución.
3. Se asigna un ticket (timestamp) que identifica la solicitud.
4. La respuesta inmediata solo confirma la recepción del comando, no su ejecución exitosa.
5. Para conocer el estado de ejecución, se debe consultar el ticket recibido usando el comando `CES`.

### Consulta LIST (Consulta de Datos Internos)

El comando LIST permite acceder a información almacenada en las bases de datos internas del sistema FSM. Es útil para inspeccionar secuencias disponibles, logs de ejecución, tablas de mensajes y otras configuraciones. La consulta no modifica el estado del sistema y está basada en sintaxis SQL.

#### Sintaxis

- **Consulta**:

  ```txt
  LIST/XXXX[/YYYY]
  ```

  - `XXXX`: Nombre de la tabla o consulta SQL a ejecutar.
  - `YYYY` (opcional): Nombres de columnas separados por comas a seleccionar. Si no se especifica, se seleccionan todas las columnas.

- **Respuesta**:

  ```html
  %d<br><code>%s</code>||;||<br>
  ```

  - `%d`: `0` si el comando fue aceptado, el código de error si hubo un problema.
  - `%s`: Datos de la consulta en formato **List Form**.

#### Detalles Técnicos

- **Función interna:** `SQL`
  - Genera la consulta a la base de datos: `SELECT YYYY FROM XXXX`. Más información en: [https://sqlite.org/lang_select.html](https://sqlite.org/lang_select.html)
- **Tablas utiles**:
  - **SEQUENCES**  
    Secuencias de comandos de la FSM.
  - **MSG**  
    Tabla de decodificación de mensajes codificados. Campos:
    - `ERROR` (INTEGER): Código de mensaje que la aplicación responde a todas las consultas y comandos.
    - `ID` (INTEGER): Código adicional, utilizado para decodificar fallas de hardware.
    - `FUNCTION` (STRING): Proceso propietario de este mensaje, nombre de la función.
    - `FSTRING` (TEXT): Cuerpo del mensaje.
    - `COMMENT` (TEXT): Información adicional, por ejemplo, acciones a seguir.
  - **CLOG**  
    Log de ejecución de sesiones. Campos:
    - `TIME` (REAL): Momento en que se registró el mensaje, en segundos desde el 01/01/1900.
    - `STEP` (INTEGER): Referencia a SEQUENCES.
    - `FAULT` (INTEGER): Código de falla.
    - `RESULT` (TEXT): Resultado de la operación.
    - `SRC` (TEXT): Fuente del mensaje.
  - **COM**  
    Cadenas de formato de respuesta del protocolo.

#### Ejemplo de Uso

- Consulta de comandos disponibles: `http://192.168.0.160:8081/REST/HTTP_CMD/?LIST/SEQUENCES/DISTINCT SEQUENCE`
- Respuesta exitosa:

  ```html
  0<br><code>SomeEvent;<br>Init;<br>SyncMode;<br>Amplification;<br>Watchdog;<br>GoToFault;<br>Stop;<br>Fire;<br>EnMode;<br></code>
  ```

### Consulta DATA (Consulta de Datos de Sensores)

El comando `DATA` permite consultar lecturas de sensores registradas por el sistema FSM. Los datos están organizados por canales, y cada canal representa una fuente distinta de información (por ejemplo, sensores físicos o registros internos). Los datos se almacenan en la tabla `DLOG` y deben consultarse con frecuencia para evitar pérdida de información.

#### Sintaxis

- **Consulta**:

  ```text
  DATA/<channel_number>[/FromTime]
  ```

  - `<channel_number>`: Número del canal del cual se desean obtener los datos.
  - `[FromTime]` (opcional): Marca de tiempo a partir de la cual se desean obtener los datos. Si no se especifica, se obtienen todos los datos del canal.
- **Respuesta**:

  ```html
  %d<br><code>%s</code>||;|<br>
  ```

  - `%d`: `0` si el comando fue aceptado, el código de error si hubo un problema.
  - `%s`: Datos del canal en formato **List Form**.

#### Detalles Técnicos

- **Función interna:** `SQLdata`
  - Genera la consulta a la base de datos: `SELECT TIME, DATA FROM DLOG WHERE CHAN = <channel_number> AND TIME > <FromTime>`
- **Tabla DLOG**:
  - Almacena datos de sensores en tiempo real.
  - Campos:
    - `TIME` (INTEGER): Marca de tiempo de los datos. Es un valor entero que representa lecturas del temporizador local, donde cada unidad equivale a 1 microsegundo (1 μs). El timestamp es relativo al sistema y no tiene un valor absoluto significativo.
    - `CHAN` (INTEGER): Canal de registro. Los datos provenientes de diferentes fuentes se organizan en canales separados. El número de canal se asigna durante la inicialización mediante el comando `logstart` (ver columna VALUE en la tabla SEQUENCES).
    - `DATA` (REAL): Lecturas reales en formato de número flotante de doble precisión (double float).
- Para no perder datos, deben consultarse con mayor frecuencia que la antigüedad máxima de los mismos en la tabla. Justificacion: La tabla de datos almacena un total de 5000 registros. A la tasa máxima de registro, por ejemplo, 5 sensores x 1000 Hz de frecuencia, el búfer conserva datos por un máximo de un segundo.
- Para no repetir datos de un canal debe usar primero la consulta `DATA/ChannelNo`. Posteriormente, se debe ciclar la consulta `DATA/ChannelNo/FromTime`, donde `FromTime` es el timestamp del último registro de datos recibido.

#### Ejemplo de Uso

- Consulta de datos del canal 2: `http://192.168.0.160:8081/REST/HTTP_CMD/?DATA/2`
- Respuesta:

  ```html
  0<br><code>1631885132;0.000000;<br>1631885509;0.000000;<br>1631885881;0.000000;<br>1631886255;0.000000;<br>1631886631;0.000000;<br>1631887004;0.000000
  ```

#### Consulta `RDVAR` (Lectura de Variables del Sistema)

El comando `RDVAR` permite consultar el valor actual de una **variable de proceso** del sistema FSM. Estas variables son de solo lectura.

#### Sintaxis

- **Consulta**:

  ```text
  RDVAR/<variable_name>
  ```

  - `<variable_name>`: Nombre de la variable a consultar. Puede ser:
    - **State**: Estado actual de la FSM (por ejemplo, `Idle`, `Busy`, `Error`).
    - **LogBlab**: Nivel de registro del sistema (0 para errores, 2 para todos los pasos).
    - **x**: Variable utilizada para pasar parámetros de comando. Por ejemplo, el comando `EXE/Amplification/50` asigna el valor 50 a la variable `x` y ejecuta la secuencia 'Amplification'.
    - **ProductID**: Identificador del tipo de producto.
    - **ProductSN**: Número de serie del producto.
- **Respuesta**:

  ```html
  %d<br>%s <br>%s
  ```

  - `%d`: `0` si el comando fue aceptado, el código de error si hubo un problema.
  - `%s`: Valor de la variable.
  - `%s`: Tipo de la variable (por ejemplo, `string`, `integer`, `float`).

#### Detalles Técnicos

- **Función interna:** RetTrueValue

#### Ejemplo de Uso

- Consulta del número de serie del producto: `http://192.168.0.160:8081/REST/HTTP_CMD/?RDVAR/ProductSN`
- Respuesta:

  ```html
  0<br>"001"
  ```

### Comando `CES` (Estado de Ejecución de Comando)

El comando `CES` (Command Execution Status) permite consultar el estado de un comando que está en ejecución o que ya finalizó, usando su ticket (timestamp asignado al enviar el comando con EXE). Si no se indica un ticket, devuelve el estado del último comando ejecutado (el más reciente en la cola), aunque no necesariamente el enviado por el usuario.

#### Sintaxis

- **Consulta**:

  ```text
  CES[/<ticket>]
  ```

  - `<ticket>` (opcional): Timestamp del comando enviado con `EXE`. Si no se especifica, se consulta el estado del último comando ejecutado.

- **Respuesta**:

  ```html
  %d<br>%d<br>%d<br>%s <br>%s <br>%f
  ```

  - `%d`: `0` si el comando fue aceptado, el código de error si hubo un problema.
  - `%d`: Código de estado de ejecución del comando.
    - `-3`: El comando fue puesto en la cola de ejecución.
    - `-2`: El comando fue recibido de la cola por la FSM.
    - `-1`: El comando está en ejecución.
    - `0`: El comando finalizó exitosamente.
    - `>0`: El comando finalizó con error (el valor indica el tipo de error).
  - `%d`: Índice de paso (IND) de la secuencia.
    - Corresponde al valor de la columna IND de la secuencia.
    - Permite identificar en qué paso se encuentra la ejecución o cuál fue el último paso ejecutado.
  - `%s`: Resultado de la ejecución del paso de la secuencia.
    - En ciclos de espera prolongados, puede mostrar resultados intermedios útiles para el monitoreo (por ejemplo, temperatura actual).
    - Palabras clave en el resultado:
      - **GoToFault**: La secuencia se detuvo y se envió el comando 'GoToFault' a la cola. El ticket del comando original ya no mostrará el estado actualizado.
      - **Skipping rest**: La secuencia se detuvo y se omitieron los pasos restantes. No hay cambios de estado.
      - **Ignoring error**: No hay consecuencias, salvo que el último paso falló.
  - `%s`: Fuente del comando.
    - Indica el origen del comando, por ejemplo, `HTTP_CMD.vi` para comandos remotos.
  - `%f`: Fecha y hora de la última actualización del estado del comando.

#### Detalles Técnicos

- **Función interna:** checkID

#### Ejemplo de Uso

- Consulta del estado de ejecución del comando 'Fire' con ticket: `http://192.168.0.160:8081/REST/HTTP_CMD/?CES/3574823433.061258`
- Respuesta, comando exitoso:

  ```html
  0<br>0<br>142<br>%22Idle%22 <br>HTTP_CMD.vi <br>09:39:30.694 2017.04.21
  ```

- Respuesta, ocurrió un error:

  ```html
  0<br>310<br>79<br>Next:%20Skipping%20rest%20 <br>HTTP_CMD.vi <br>09:42:21.460 2017.04.21
  ```
