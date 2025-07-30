# Control de Máquina de Estados LazServ

## Descripción del Control del Láser

* [cite_start]El control del láser se centra en una máquina de estados finitos (FSM) impulsada por eventos[cite: 2].
* [cite_start]La FSM es una aplicación que se ejecuta en la placa LazServ, la cual está integrada en el sistema láser[cite: 3].
* [cite_start]La FSM misma recibe comandos de forma remota a través de una interfaz LAN o RS232 (no cubierta en este manual)[cite: 4].

## Máquina de Estados

### [cite_start]Representación de la Máquina de Estados [cite: 6]
* **Estados**:
    * [cite_start]Solo se permite un estado en un momento dado[cite: 28].
    * [cite_start]La FSM puede cambiar de un estado a otro en respuesta a un comando remoto[cite: 29].
    * [cite_start]El estado en sí mismo es una variable que se puede leer en cualquier momento, pero no se puede escribir[cite: 30].
    * [cite_start]Los estados representados en el diagrama incluyen: "Idle" [cite: 8][cite_start], "Prepared" [cite: 14][cite_start], "Armed" [cite: 19][cite_start], "Triggered" [cite: 22] [cite_start]y "Error"[cite: 17].
* **Transiciones**:
    * [cite_start]Solo se permite una transición en un momento dado[cite: 32].
    * [cite_start]Los eventos se publican en una cola mientras la FSM está en transición[cite: 33].
    * [cite_start]Una transición exitosa conducirá al estado planificado; una transición fallida puede dejar el estado sin cambios o generar un evento "GoToFault"[cite: 34].
    * La transición se compone como una secuencia lineal de comandos escritos en un lenguaje de script simple. [cite_start]Las secuencias se enumeran en la tabla SEQUENCES[cite: 35].
    * [cite_start]El tiempo que dura una transición no está limitado; la aplicación externa puede sondear el estado actual de la FSM[cite: 36].
    * [cite_start]Las transiciones incluyen: "rst_n" [cite: 7][cite_start], "Prepare" [cite: 9][cite_start], "Stop" [cite: 9, 11, 23, 24][cite_start], "ErrorAck" [cite: 10][cite_start], "GoToFault" [cite: 12, 15, 18, 20][cite_start], "SyncTest" [cite: 13][cite_start], "Arm" [cite: 16][cite_start], "Trigger" [cite: 21] [cite_start]y "ManualTrigger"[cite: 25].

## Implementación de la Máquina de Estados

* [cite_start]La máquina de estados se implementa como una aplicación ejecutable de Linux[cite: 38].
* [cite_start]La aplicación maneja el control y la comunicación de la FSM[cite: 39].
* [cite_start]La aplicación de la FSM está escrita en LUA[cite: 40].

## Servicios de Comunicación

* [cite_start]Para manejar la comunicación entre la FSM y el controlador remoto, se ejecuta un servidor HTTP en el puerto 8081 en la placa de control[cite: 42].
* [cite_start]La API REST sobre TCP/IP permite controlar la FSM de forma remota[cite: 43].
* [cite_start]Los comandos y respuestas REST se pueden ingresar/ver mediante un navegador ordinario[cite: 44].
* [cite_start]Además del servidor REST en la PC de control, se ejecutan servidores adicionales en los puertos 80 y 8080 del controlador de comunicación[cite: 45].
* [cite_start]El servidor HTTP en el puerto 80 se utiliza para la configuración de la comunicación[cite: 46, 47].
* [cite_start]El servidor HTTP en el puerto 8080 admite la API REST y se utiliza para la comunicación directa con módulos individuales del sistema[cite: 49].
* [cite_start]Los servidores 80 y 8080 utilizan diferentes protocolos que no están cubiertos en este manual[cite: 51].
* [cite_start]La FSM se comunica con el hardware del láser a través del puerto COM (virtual o genuino), o a través de LAN/WLAN[cite: 52].

## Diagrama de Control del Láser

El diagrama de control del láser muestra los siguientes componentes:
* [cite_start]**Sistema de archivos flash USB externo**: Contiene `SQLite file LOG.db` [cite: 57] [cite_start]y `SQLite file unilaz.db` [cite: 58][cite_start], así como `User data file(s)`[cite: 56].
* [cite_start]**Sistema de archivos flash interno**: Contiene `SQLite file LOG.db` [cite: 62] [cite_start]con `Messages log` [cite: 63] [cite_start]y `SQLite file unilaz.db` [cite: 68] que incluye:
    1.  [cite_start]`State mashine configuration` (configuración de la máquina de estados)[cite: 69].
    2.  [cite_start]`User interface configuration` (configuración de la interfaz de usuario)[cite: 69].
    3.  [cite_start]`Protocol configuration` (configuración del protocolo)[cite: 69].
    4.  [cite_start]`Error messages decoding` (decodificación de mensajes de error)[cite: 70].
* [cite_start]`HMI library (DPU etc)`[cite: 64].
* [cite_start]`LazServ, lua engine`[cite: 65].
* [cite_start]`State machine engine` (motor de la máquina de estados)[cite: 71].
* **Bases de datos SQLite en memoria**:
    * [cite_start]`CLOG table` (historial de ejecución): `SQLite:memory:`[cite: 74, 75].
    * [cite_start]`TLOG table` (estado de ejecución de la FSM): `SQLite:memory:`[cite: 76].
    * [cite_start]`DLOG table` (datos de medición, mensajes de fallos de HW): `SQLite:memory:`[cite: 77, 78].
* [cite_start]`Serial protocol server a la REST`[cite: 66, 67].
* [cite_start]`Web server REST, Web client IoT API`[cite: 72, 73].
* [cite_start]`Socket CAN??`[cite: 79].
* [cite_start]**Conexiones**: `USB RS232` [cite: 80][cite_start], `LAN` [cite: 81][cite_start], `CAN`[cite: 87].
* [cite_start]`User control application (Windows, Linux, Android etc)`[cite: 82].
[cite_start]`IoT cloud`[cite: 83].
* [cite_start]`Laser module 1, 2, 3`[cite: 88].
* [cite_start]`Laser XLXXXX`[cite: 89].

## [cite_start]Bloques Esenciales [cite: 90]

1.  [cite_start]**Motor de la máquina de estados**: Se emplea un ciclo infinito: recibir comandos, procesar eventos, ejecutar secuencias, publicar resultados[cite: 91].
2.  [cite_start]**Servidor web/REST**: Procesa las solicitudes GET de REST y compone los datos de retorno[cite: 92]. [cite_start]Toda la comunicación entre la aplicación del usuario y la FSM del láser pasa por este servidor[cite: 93].
3.  [cite_start]**Base de datos de configuración, SQLite file `unilaz.db`**[cite: 94].
4.  [cite_start]**Base de datos de registro de sesión, SQLite file `log.db`**: Registra mensajes de error en modo normal y todos los pasos en modo depuración[cite: 94].
5.  [cite_start]**Base de datos de estado de ejecución, SQLite memory file, TLOG table**: Contiene actualizaciones de estado sobre la ejecución de secuencias[cite: 94].
6.  [cite_start]**Base de datos de datos, SQLite memory file, DLOG table**[cite: 94].
    * [cite_start]Los archivos SQLite son accesibles a través de consultas especializadas[cite: 94].

## Solicitudes de Interfaz Remota/Usuario

* La FSM comienza ejecutando la secuencia `Init`. [cite_start]Después de que la secuencia `Init` finaliza con éxito, la FSM entra en modo de espera de eventos[cite: 94].
* [cite_start]Los eventos son generados por comandos remotos[cite: 94].
* [cite_start]Formato de URL de solicitud/comando: `protocol://host/REST/HTTP_CMD/query`[cite: 94].
* [cite_start]Tanto las solicitudes como los comandos utilizan el protocolo HTTP GET, por lo tanto, un navegador de internet es suficiente para probar la comunicación y el control[cite: 94].
    * [cite_start]`protocol`: `http`[cite: 94].
    * [cite_start]`host`: `xxx.XXX.XXX.XXX:8081`[cite: 94].
    * [cite_start]`REST/HTTP_CMD` - cadena de identificación de la FSM[cite: 94].
    * [cite_start]`query` - comando o solicitud de parámetro[cite: 94].

### Formato de Consulta

* La consulta comienza con un símbolo de interrogación (?). [cite_start]En la descripción siguiente, se omite el '?'[cite: 94].
* [cite_start]El '?' es seguido por la palabra `query` o `command` y los parámetros separados por el símbolo '/'[cite: 94].
    * `query`: solicitud de estado de ejecución, variables o datos del sensor. [cite_start]La consulta no cambia el estado de la FSM[cite: 94].
    * [cite_start]`command`: instrucciones para la FSM que alterarán el estado[cite: 94].

### Uso de Comandos/Consultas

#### [cite_start]`LIST` query [cite: 94]
* [cite_start]Devuelve los resultados de la consulta `SELECT` de los archivos de base de datos SQLite `unilaz.db` y `log.db`[cite: 94].
* [cite_start]El uso más obvio del comando `LIST` es leer el registro de mensajes de ejecución o leer la lista de mensajes codificados[cite: 94].
* [cite_start]Uso del comando `LIST`: `LIST/XXXX[/YYYY]`[cite: 94].
    * [cite_start]Esto resultará en una consulta a la base de datos: `SELECT YYYY FROM XXXX`[cite: 94].
    * `YYYY` son nombres de columnas separados por comas. `YYYY` se reemplazará por `*` en caso de que no se suministre ningún parámetro, lo que resultará en la lista de todas las columnas. [cite_start]Se puede usar la declaración `DISTINCT`[cite: 94].
    * `XXXX` debe comenzar con el nombre de la tabla, pero no se limita a ella. Se pueden usar las declaraciones `GROUP BY`, `ORDER BY`, `LIMIT`. [cite_start]Consultar el lenguaje SQLite para obtener detalles `https://sqlite.org/lang_select.html`[cite: 94].
* Nombres de tabla:
    * [cite_start]`SEQUENCES`: secuencias de comandos FSM[cite: 94].
    * `MSG`: tabla de decodificación de mensajes codificados. Campos: `ERROR` (INTEGER) - código de mensaje al que la aplicación responde a todas las consultas y comandos; `ID type` (INTEGER) - código adicional, utilizado para decodificar fallas de hardware; `FUNCTION type` (STRING) - proceso, propietario de este mensaje, nombre; `FSTRING type` (TEXT) - cuerpo del mensaje; [cite_start]`COMMENT type` (TEXT) - información adicional, por ejemplo, qué hacer a continuación[cite: 94].
    * `CLOG`: registro de ejecución de sesión. Campos: `TIME` (REAL) - tiempo en que se registró el mensaje en segundos transcurridos desde 1900 01 01; [cite_start]`STEP` (INTEGER), `FAULT` (INTEGER), `RESULT` (TEXT), `SRC` (TEXT)[cite: 94].
* Ejemplos de consulta:
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?LIST/MSG` - lista de mensajes codificados[cite: 94].
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?LIST/SEQUENCES/DISTINCT SEQUENCE` - para ver todos los comandos FSM disponibles[cite: 94].
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?LIST/CLOG` - para obtener el registro de ejecución[cite: 94].
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?LIST/CLOG WHERE TIME > 3574141740.945` - para obtener el registro de ejecución a partir de cierto momento[cite: 94].

#### [cite_start]`DATA` query [cite: 96]
* [cite_start]Devuelve los resultados de la consulta `SELECT` de la tabla de datos SQLite[cite: 97]. La tabla de datos contiene lecturas de medición de sensores e informes sobre cambios en el valor de los registros. [cite_start]Los informes sobre cambios en el registro 'Error Code' se publican en esta tabla[cite: 98].
* [cite_start]La tabla de datos está organizada en tres columnas[cite: 98]:
    * `TIME`: marca de tiempo de los datos. Lecturas del temporizador local, número entero. Una cuenta corresponde a 1us. [cite_start]La marca de tiempo depende del sistema sin un valor absoluto significativo[cite: 98].
    * `CHAN`: canal de registro. Los datos de diferentes fuentes se organizan en canales separados. [cite_start]El número de canal se asigna durante la inicialización mediante el comando `logstart`, ver columna `VALUE` de la tabla `SEQUENCES`[cite: 98].
    * [cite_start]`DATA`: lecturas reales en formato de coma flotante doble[cite: 98].
* [cite_start]Formato del comando: `DATA/ChannelNo[/FromTime]`[cite: 98].
* Ejemplos de consulta:
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?DATA/2` - obtener todos los datos del canal No 2[cite: 98].
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?DATA/2/1458866649` - datos del canal No 2, donde `TIME > 1458866649`[cite: 98].
* [cite_start]La tabla de datos mantiene 5000 registros en total[cite: 98]. [cite_start]A la tasa máxima de registro, por ejemplo, 5 sensores x 1000Hz de frecuencia, el búfer mantiene datos de un segundo como máximo de antigüedad[cite: 98]. [cite_start]Los datos deben consultarse con más frecuencia que la antigüedad máxima de los datos para mantener la coherencia[cite: 98].
* [cite_start]El software de aplicación que necesite un conjunto de datos coherente del canal debe usar primero la consulta `DATA/ChannelNo`[cite: 98]. Posteriormente, la consulta `DATA/ChannelNo/FromTime` debe ser cíclica. [cite_start]Donde `FromTime` es la marca de tiempo del último registro de datos recibido[cite: 98].

#### [cite_start]`EXE` command [cite: 98]
* [cite_start]Publica un comando FSM en la cola de ejecución[cite: 98].
* [cite_start]Al publicar un comando en la cola, se le asigna un ticket[cite: 98]. Como ticket sirve el tiempo real de recepción del comando. [cite_start]El ticket se usa posteriormente para recuperar el estado de ejecución del comando[cite: 98].
* [cite_start]El estado real del comando no se conoce en el momento de la publicación, por lo tanto, una respuesta positiva significa el éxito de la publicación, pero no la ejecución en sí[cite: 98].
* [cite_start]Consultar la consulta `CES` para obtener el estado de ejecución[cite: 98].
* [cite_start]Formato del comando: `EXE/Command[/Parameter]`[cite: 98].
* Ejemplos de comando:
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?EXE/Stop`[cite: 98].
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?EXE/Fire`[cite: 98].
* [cite_start]Los comandos y parámetros disponibles se enumeran en la documentación del producto[cite: 98].

#### [cite_start]`RDVAR` query [cite: 98]
* [cite_start]Devuelve el valor de una variable de proceso[cite: 98].
* [cite_start]Las variables de proceso se utilizan para pasar parámetros entre los pasos de la secuencia[cite: 98].
* [cite_start]Las variables son de solo lectura desde el punto de vista del control remoto[cite: 98].
* [cite_start]Hay varias variables predefinidas[cite: 98]:
    * [cite_start]`'State'` - estado actual de la FSM[cite: 98].
    * `'LogBlab'` - extensión del registro. [cite_start]`0` - solo se registran errores, `2` - se registran todos los pasos de la secuencia[cite: 98].
    * `'x'` - variable utilizada para pasar el parámetro de comando. [cite_start]Por ejemplo, el comando `EXE/Amplification/50` hace lo siguiente: establece la variable `x` en 50 y realiza la secuencia 'Amplification'[cite: 98].
    * [cite_start]`'ProductID'` - tipo de producto[cite: 98].
    * [cite_start]`'ProductSN'` - número de serie[cite: 98].
* Ejemplo de consulta `RDVAR`:
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?RDVAR/State` - devuelve el estado actual[cite: 98].
    * [cite_start]`http://192.168.0.160:8081/REST/HTTP_CMD/?RDVAR/LogBlab` - devuelve la extensión del registro[cite: 98].

#### [cite_start]`CES` query [cite: 98]
* [cite_start]Devuelve el estado de un comando que se está ejecutando o ha finalizado[cite: 99].
* [cite_start]Formato del comando: `CES[/Timestamp]`[cite: 99].
* [cite_start]`Timestamp` es el marcador del comando y se recibe en la respuesta del comando `EXE`[cite: 100].
* [cite_start]Ejemplo de comando: `http://192.168.0.160:8081/REST/HTTP_CMD/?CES/3574677021.391924`[cite: 102].
* [cite_start]Un comando sin `Timestamp` devuelve el estado del último comando recibido de la cola[cite: 103].
* [cite_start]La consulta `CES` devuelve un código de estado de la consulta y los siguientes parámetros de ejecución del comando[cite: 104]:
    1.  **Código de estado de ejecución del comando**:
        * [cite_start]`-3` - comando publicado en la cola[cite: 106].
        * [cite_start]`-2` - comando recibido de la cola por la FSM[cite: 107].
        * [cite_start]`-1` - comando en ejecución[cite: 108].
        * [cite_start]`0` - comando finalizado con éxito[cite: 109].
        * [cite_start]`>0` - comando finalizado con error[cite: 110].
    2.  [cite_start]**Índice del paso (`IND`)**: Índice (valor de la columna IND) del paso actual en ejecución o el último paso para un comando finalizado[cite: 111]. [cite_start]Conocer el valor `IND` permite comprender lo que está haciendo la FSM en ese momento[cite: 112].
    3.  [cite_start]**Resultado**: Resultado de la ejecución del paso de la secuencia[cite: 113]. [cite_start]En ciclos de espera largos, ver un resultado intermedio puede ayudar a comprender el proceso en sí[cite: 114]. [cite_start]El resultado guarda información importante sobre las consecuencias de un error en la ejecución de la secuencia[cite: 115]. [cite_start]Las palabras clave que explican las consecuencias son las siguientes "Next:" la cadena puede ser[cite: 115]:
        * [cite_start]`GoToFault`: la ejecución de la secuencia se termina en este punto y el comando 'GoToFault' se publica en la cola[cite: 116]. En general, el resultado será un estado que indica algún fallo. [cite_start]`GoToFault` será el nuevo comando y el ticket antiguo no se mostrará[cite: 117].
        * [cite_start]`Skipping rest`: la ejecución de la secuencia se termina en este punto, los pasos restantes de la secuencia se omiten[cite: 118]. En general, el resultado no tendrá cambios en el estado. [cite_start]Los `guards` generan este error[cite: 119].
        * [cite_start]`Ignoring error`: no habrá consecuencias, excepto que el último paso salió mal[cite: 120].
    4.  [cite_start]**Fuente**: `HTTP_CMD.vi` para el comando de control remoto[cite: 121].
    5.  [cite_start]**Marca de tiempo de la última operación**[cite: 122].

## [cite_start]Respuestas a Consultas [cite: 123]

* [cite_start]Las respuestas a las consultas se formatean según la información de la columna `RES_HTML` en la tabla `COM`, archivo `unilaz.db`[cite: 124].

| COM_NAME | FUNCTION | RES_PAR_COUT | RES_HTML | DESCRIPTION |
|---|---|---|---|---|
| EXE | exeSEQM | 2 | `%d<br><a href=""?CES/%d"">Check status</a>` | 2. [cite_start]Command ticket (timestamp) [cite: 125] |
| RDVAR | Ret TrueValue | 2 | `%d<br>%s <br>%s` | 2. [cite_start]Variable value 3. Type [cite: 125] |
| CES | checkID | 6 | `%d<br>%d<br>%d<br>%s <br>%s <br>%f` | 2. [cite_start]Command execution status code 3. Step index (IND) 4. Result 5.Source 6. Last operation timestamp [cite: 125] |
| LIST | SQL | 2 | `%d<br><code>%s</code>||;||<br>` | 2. [cite_start]SQL query result in list form [cite: 125] |
| DATA | SQLdata | 2 | `%d<br><code>%s</code>||;|<br>` | 2. [cite_start]SQL query result in list form [cite: 125] |

[cite_start]Donde[cite: 126]:
* [cite_start]`COM_NAME`: nombre de la consulta/comando tal como aparece en la consulta[cite: 127].
* `FUNCTION`: nombre de la función interna. [cite_start]Debe dejarse sin cambios, porque este es el enlace a la función real[cite: 128].
* [cite_start]`RES_PAR_COUT`: parámetros que se pasan a la función de formato en respuesta a la consulta[cite: 129].
* [cite_start]`RES_HTML`: cadena de formato que especifica cómo se desea que la función convierta los argumentos de entrada en la cadena resultante[cite: 130].
* `DESCRIPTION`: descripciones de los parámetros. [cite_start]El primer parámetro siempre es el código de respuesta, por lo tanto, se omite[cite: 131].

[cite_start]Reglas generales[cite: 132]:
* [cite_start]El primer parámetro siempre es el código de respuesta de la consulta[cite: 133]. [cite_start]Un código cero significa que la consulta/comando fue aceptado y los resultados siguientes son válidos[cite: 133]. [cite_start]Un valor distinto de cero significa que la consulta no puede devolver resultados significativos debido al error que representa el código[cite: 134].
* [cite_start]Los parámetros siguientes son los resultados reales de la consulta[cite: 135].
* [cite_start]Las respuestas a las consultas tienen un formato mínimo, solo para mantener la legibilidad en los navegadores modernos[cite: 136]. [cite_start]Al cambiar las cadenas de formato, existe la posibilidad de cumplir con muchos estándares de codificación de información: XML, JSON, HTML[cite: 137].
* [cite_start]El formato de respuesta es sencillo para las consultas `EXE`, `RDVAR`, `CES`; solo hay una cadena de formato[cite: 138].
* [cite_start]El formato de respuesta para las consultas `LIST` y `DATA` se divide en dos pasos[cite: 139]:
    1.  [cite_start]`%d<br><code>%s</code>` - es el envoltorio general[cite: 140]. [cite_start]Donde `%d` es el código de respuesta y `%s` es el cuerpo de la respuesta[cite: 141].
    2.  [cite_start]El símbolo `''` divide el envoltorio del formato de fila[cite: 142].
* Las reglas de formato de fila son:
    1.  [cite_start]**Consulta `DATA`**: Hay tres cadenas separadas por el símbolo ' ': 1. inicio de fila (cadena vacía) 2. separador (punto y coma) 3. terminador de fila (salto de línea único)[cite: 144].
    2.  [cite_start]**Consulta `LIST`**: Hay cuatro cadenas separadas por el símbolo 'l': 1. inicio de columna (cadena vacía) 2. separador de columna (punto y coma) 3. inicio de fila (cadena vacía) 3. terminador de fila (salto de línea único)[cite: 145].

## Ejemplos de Respuesta

* [cite_start]**Consulta de comandos disponibles**: `http://192.168.0.160:8081/REST/HTTP_CMD/?LIST/SEQUENCES/DISTINCT SEQUENCE` [cite: 147]
    * **Respuesta**: `0<br><code>SomeEvent; <br>Init; <br>SyncMode; <br>Amplification; <br>Watchdog; <br>GoToFault; <br>Stop; <br>Fire; <br>EnMode; [cite_start]<br></code> [cite: 148, 149]
* [cite_start]**Consulta de datos del canal 2**: `http://192.168.0.160:8081/REST/HTTP_CMD/?DATA/2` [cite: 149]
    * **Respuesta**: `<br><code>1631885132;0.000000; <br>1631885509;0.000000;<br>1631885881;0.000000;<br>1631886255;0.000000; <br>1631886631;0.000000; [cite_start]<br></code> [cite: 150, 151]
* [cite_start]**Comando 'Stop'**: `http://192.168.0.160:8081/REST/HTTP_CMD/?EXE/Stop` [cite: 151]
    * [cite_start]**Respuesta**: `0<br><a href="?CES/3575601570403">Check status</a>` [cite: 152, 153]
* [cite_start]**Consulta del estado de ejecución del comando 'Fire' con ticket**: `http://192.168.0.160:8081/REST/HTTP_CMD/?CES/3574823433.061258` [cite: 154]
    * [cite_start]**Respuesta, comando exitoso**: `0<br>0<br>142<br>%22Idle%22 <br>HTTP CMD.vi <br>09:39:30.694 2017.04.21` [cite: 155, 156]
    * [cite_start]**Respuesta, error ocurrido**: `0<br>310<br>79<br>Next:%20Skipping%20rest%20 <br>HTTP_CMD.vi <br>09:42:21.460 2017.04.21` [cite: 157, 158]
* [cite_start]**Consulta del número de serie del producto**: `http://192.168.0.160:8081/REST/HTTP_CMD/?RDVAR/ProductSN` [cite: 159]
    * [cite_start]**Respuesta**: `0<br>"001"` [cite: 160, 161]

## [cite_start]Manejo de Errores y Sistema de Información [cite: 162]

[cite_start]La FSM maneja errores de las siguientes fuentes[cite: 163]:
1.  [cite_start]Módulo de ejecución de la FSM[cite: 164].
2.  [cite_start]Red CAN[cite: 165].
3.  [cite_start]Servidor HTTP[cite: 166].
4.  [cite_start]Módulos de hardware[cite: 167].

* [cite_start]Cada paso individual de la secuencia tiene asignado algún tipo de manejador de errores[cite: 168].
* [cite_start]En caso de que el objetivo del paso no se pueda lograr, el manejador de errores realiza algunas acciones predefinidas[cite: 169].

### [cite_start]Tipos de Manejadores de Errores [cite: 170]

| Nombre | Parámetro | Acción(es) | Uso Típico |
|---|---|---|---|
| ResetErr | [vacío] | El error se borra, se publica 'Clean completion' como resultado en el registro con código de éxito | [cite_start]Se utiliza junto con el comando `waitfor` que actúa como un retardo de tiempo fijo[cite: 171]. |
| IgnoreErr | [vacío] | El error se borra, se publica 'Next: Ignore error' como resultado en el registro con código de fallo | [cite_start]Útil durante la depuración para no interrumpir la ejecución, pero ver el código de error en el registro[cite: 171]. |
| SkipRestOnErr | Opcional, código de sustitución | Se publica 'Next: Skipping rest' como resultado en el registro con el código de error original o, si se proporciona, con el código de sustitución. La ejecución de la secuencia se termina | Se utiliza en `guards` al principio de la secuencia. [cite_start]En caso de que los `guards` no se superen, no se ejecutan más pasos y el estado de la FSM permanece sin cambios[cite: 171]. |
| FaultOnErr | Opcional, código de sustitución | El evento 'GoToFault' se publica en la cola, se publica 'Next: GoToFault' como resultado en el registro con el código de error original o, si se proporciona, con el código de sustitución. La secuencia actual se termina, la secuencia `GoToFault` se recupera de la cola y se ejecuta | [cite_start]Se utiliza para dirigir la FSM al modo de fallo[cite: 171]. |

* [cite_start]El código de sustitución en `SkipRestOnErr` y `FaultOnErr` se utiliza para reemplazar el mensaje de error estándar con información relacionada con el sistema particular[cite: 172].
* [cite_start]Por ejemplo, en caso de que se verifique algún bit que representa el estado de un interbloqueo de seguridad en la secuencia, la FSM normalmente publicará un error de que este bit tiene el valor `x` en lugar del `y` requerido[cite: 173]. [cite_start]Esto hace que la resolución de problemas sea sofisticada[cite: 174].