import requests
from pg401_pyqt.controller.enums_commands import List, Exe, Rdvar
from pg401_pyqt.controller.handler_exceptions import handler_exceptions, validate_wave_params
from pg401_pyqt.controller.response_handler import parse_ces_response
from pg401_pyqt.utils.logger import logger
import time

IP = "192.168.0.160"
LAN_IP = "192.254.224.164"
IP_MOCK = "abaab562dceb.ngrok-free.app"
URL_BASE = f"https://{IP_MOCK}/REST/HTTP_CMD/?"
URL_WAVE = f"https://{IP_MOCK}/MaxiOPG/33/WaveLength"


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


def exe_wave_command(query: Exe, range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float):
    validate_wave_params(range_init_nm, range_end_nm, step_nm, time_s)
    info = []
    if range_end_nm >= range_init_nm:
        info = logic_wave_forward(query, range_init_nm, range_end_nm, step_nm, time_s)
    else:
        info = logic_wave_backward(query, range_init_nm, range_end_nm, step_nm, time_s)
    return info


def logic_wave_forward(query: Exe, range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float):

    if query != Exe.WAVELENGTH:
        logger.error("Error: la query proporcionada no es válida para longitud de onda.")
        return []

    accumulator_step = range_init_nm
    info = []
    while accumulator_step <= range_end_nm:
        try:
            url = f"{URL_BASE}{query.value}{accumulator_step:.7f}"
            response = requests.get(url)
            response.raise_for_status()
            # Respuesta del seteo en verde
            info.append(f"<span style='color:#00ff00;'>[SET] {response.text}</span>")
            logger.info(f"Longitud de onda establecida en {accumulator_step:.7f} nm")

            wave_response = requests.get(URL_WAVE)
            wave_response.raise_for_status()
            # Respuesta del estado en verde
            info.append(f"<span style='color:#00ff00;'>[STATE] {wave_response.text}</span>")
        except requests.exceptions.RequestException as e:
            handler_exceptions(e)
            info.append(f"<span style='color:red;'>Error en {accumulator_step} nm: {e}</span>")
            break
        info.append("<br>")  # Separador visual
        time.sleep(time_s)
        accumulator_step += step_nm
    return info


def logic_wave_backward(query: Exe, range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float):

    if query != Exe.WAVELENGTH:
        logger.error("Error: la query proporcionada no es válida para longitud de onda.")
        return []

    accumulator_step = range_init_nm
    info = []
    while accumulator_step >= range_end_nm:
        try:
            url = f"{URL_BASE}{query.value}{accumulator_step:.7f}"
            response = requests.get(url)
            response.raise_for_status()
            info.append(f"<span style='color:#00ff00;'>[SET] {response.text}</span>")
            logger.info(f"Longitud de onda establecida en {accumulator_step:.7f} nm")

            wave_response = requests.get(URL_WAVE)
            wave_response.raise_for_status()
            info.append(f"<span style='color:#00ff00;'>[STATE] {wave_response.text}</span>")
        except requests.exceptions.RequestException as e:
            handler_exceptions(e)
            info.append(f"<span style='color:red;'>Error en {accumulator_step} nm: {e}</span>")
            break
        info.append("<br>")
        time.sleep(time_s)
        accumulator_step -= step_nm
    return info
