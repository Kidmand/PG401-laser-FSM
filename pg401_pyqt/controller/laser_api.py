import requests
from pg401_pyqt.controller.enums_commands import List, Exe, Rdvar
from pg401_pyqt.controller.handler_exceptions import handler_exceptions, validate_wave_params
from pg401_pyqt.controller.response_handler import parse_ces_response
from pg401_pyqt.utils.logger import logger
import time

# Configuraciones de red
#IP = "192.168.0.160"
#LAN_IP = "192.254.224.164"
#IP_MOCK = "abaab562dceb.ngrok-free.app"
#URL_BASE = f"https://{IP_MOCK}/REST/HTTP_CMD/?"
#URL_WAVE = f"https://{IP_MOCK}/MaxiOPG/33/WaveLength"
LAN_IP = "169.254.224.164"
URL_BASE = f"http://{LAN_IP}:8081/REST/HTTP_CMD/?"
URL_WAVE = f"http://{LAN_IP}:8080/MaxiOPG/33/WaveLength"

# Configuración activa - Mock Server Local
#IP_MOCK_LOCAL = "localhost"
# URL_BASE = f"http://{IP_MOCK_LOCAL}:8080/REST/HTTP_CMD/?"
# URL_WAVE = f"http://{IP_MOCK_LOCAL}:8080/MaxiOPG/33/WaveLength"


def list_command(query: List, time: float = None):
    try:
        if (query == List.CLOG_WHERE):
            response = requests.get(URL_BASE + query.value + str(time))
        else:
            response = requests.get(URL_BASE + query.value)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exceptions(e)


def exe_command(query: Exe, aplification: int = None):
    try:
        if (query == Exe.AMPLIFICATION):
            response = requests.get(URL_BASE + query.value + str(aplification))
        else:
            response = requests.get(URL_BASE + query.value)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exceptions(e)


def rdvar_command(query: Rdvar):
    try:
        response = requests.get(URL_BASE + query.value)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exceptions(e)


def data_command(channelNo: int, time: float = None):
    try:
        if (time is not None):
            response = requests.get(
                URL_BASE + "DATA/" + str(channelNo) + "/" + str(time))
        else:
            response = requests.get(URL_BASE + "DATA/" + str(channelNo))
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exceptions(e)


def ces_command(time: float = None):
    try:
        if (time is not None):
            response = requests.get(URL_BASE + "CES/" + str(time))
        else:
            response = requests.get(URL_BASE + "CES")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exceptions(e)


def wave_command():
    try:
        response = requests.get(URL_WAVE)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exceptions(e)


def exe_wave_command(query: Exe, range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float, window=None):
    validate_wave_params(range_init_nm, range_end_nm, step_nm, time_s)
    info = []
    if range_end_nm >= range_init_nm:
        info = logic_wave_forward(query, range_init_nm, range_end_nm, step_nm, time_s, window)
    else:
        info = logic_wave_backward(query, range_init_nm, range_end_nm, step_nm, time_s, window)
    return info


def logic_wave_forward(query: Exe, range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float, window=None):

    if query != Exe.WAVELENGTH:
        logger.error("Error: la query proporcionada no es válida para longitud de onda.")
        return []

    accumulator_step = range_init_nm
    info = []
    # Usar <= con tolerancia de punto flotante para incluir el valor final exacto
    while accumulator_step <= range_end_nm + (step_nm * 0.001):
        # Verificar si se debe detener el barrido (compatible con hilo y ventana)
        if window and hasattr(window, 'stop_requested') and window.stop_requested:
            break
        if window and hasattr(window, 'stop_barrido') and window.stop_barrido:
            break
        
        # Si el próximo step superaría el rango final, ajustar al valor final exacto
        if accumulator_step > range_end_nm:
            accumulator_step = range_end_nm
        
        # Actualizar último valor procesado en el hilo
        if window and hasattr(window, 'ultimo_valor_procesado'):
            window.ultimo_valor_procesado = accumulator_step
            
        try:
            url = f"{URL_BASE}{query.value}{accumulator_step:.7f}"
            response = requests.get(url)
            response.raise_for_status()
            # Respuesta del seteo en verde
            mensaje_set = f"<span style='color:#00ff00;'>[SET] {response.text}</span>"
            info.append(mensaje_set)
            logger.info(f"Longitud de onda establecida en {accumulator_step:.7f} nm")
            
            # Enviar mensaje en tiempo real si es un hilo
            if window and hasattr(window, 'mensaje_signal'):
                window.mensaje_signal.emit(f"<pre>{mensaje_set}</pre>")

            # Pequeño delay para evitar saturar la cola de comandos del servidor
            time.sleep(0.05)  # 50ms de delay entre comandos
            
            wave_response = requests.get(URL_WAVE)
            wave_response.raise_for_status()
            # Respuesta del estado en verde
            mensaje_state = f"<span style='color:#00ff00;'>[STATE] {wave_response.text}</span>"
            info.append(mensaje_state)
            
            # Enviar mensaje en tiempo real si es un hilo
            if window and hasattr(window, 'mensaje_signal'):
                window.mensaje_signal.emit(f"<pre>{mensaje_state}</pre>")
                window.mensaje_signal.emit("<br>")
                
        except requests.exceptions.RequestException as e:
            handler_exceptions(e)
            mensaje_error = f"<span style='color:red;'>Error en {accumulator_step} nm: {e}</span>"
            info.append(mensaje_error)
            
            # Enviar mensaje de error en tiempo real si es un hilo
            if window and hasattr(window, 'mensaje_signal'):
                window.mensaje_signal.emit(mensaje_error)
            break
            
        info.append("<br>")  # Separador visual
        
        # Si ya procesamos el valor final exacto, salir del loop
        if accumulator_step >= range_end_nm:
            break
            
        time.sleep(time_s)
        accumulator_step += step_nm
    return info


def logic_wave_backward(query: Exe, range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float, window=None):

    if query != Exe.WAVELENGTH:
        logger.error("Error: la query proporcionada no es válida para longitud de onda.")
        return []

    accumulator_step = range_init_nm
    info = []
    # Usar >= con tolerancia de punto flotante para incluir el valor final exacto
    while accumulator_step >= range_end_nm - (step_nm * 0.001):
        # Verificar si se debe detener el barrido (compatible con hilo y ventana)
        if window and hasattr(window, 'stop_requested') and window.stop_requested:
            break
        if window and hasattr(window, 'stop_barrido') and window.stop_barrido:
            break
        
        # Si el próximo step superaría el rango final, ajustar al valor final exacto
        if accumulator_step < range_end_nm:
            accumulator_step = range_end_nm
        
        # Actualizar último valor procesado en el hilo
        if window and hasattr(window, 'ultimo_valor_procesado'):
            window.ultimo_valor_procesado = accumulator_step
            
        try:
            url = f"{URL_BASE}{query.value}{accumulator_step:.7f}"
            response = requests.get(url)
            response.raise_for_status()
            # Respuesta del seteo en verde
            mensaje_set = f"<span style='color:#00ff00;'>[SET] {response.text}</span>"
            info.append(mensaje_set)
            logger.info(f"Longitud de onda establecida en {accumulator_step:.7f} nm")
            
            # Enviar mensaje en tiempo real si es un hilo
            if window and hasattr(window, 'mensaje_signal'):
                window.mensaje_signal.emit(f"<pre>{mensaje_set}</pre>")

            # Pequeño delay para evitar saturar la cola de comandos del servidor
            time.sleep(0.05)  # 50ms de delay entre comandos
            
            wave_response = requests.get(URL_WAVE)
            wave_response.raise_for_status()
            # Respuesta del estado en verde
            mensaje_state = f"<span style='color:#00ff00;'>[STATE] {wave_response.text}</span>"
            info.append(mensaje_state)
            
            # Enviar mensaje en tiempo real si es un hilo
            if window and hasattr(window, 'mensaje_signal'):
                window.mensaje_signal.emit(f"<pre>{mensaje_state}</pre>")
                window.mensaje_signal.emit("<br>")
                
        except requests.exceptions.RequestException as e:
            handler_exceptions(e)
            mensaje_error = f"<span style='color:red;'>Error en {accumulator_step} nm: {e}</span>"
            info.append(mensaje_error)
            
            # Enviar mensaje de error en tiempo real si es un hilo
            if window and hasattr(window, 'mensaje_signal'):
                window.mensaje_signal.emit(mensaje_error)
            break
            
        info.append("<br>")
        
        # Si ya procesamos el valor final exacto, salir del loop
        if accumulator_step <= range_end_nm:
            break
            
        time.sleep(time_s)
        accumulator_step -= step_nm
    return info
