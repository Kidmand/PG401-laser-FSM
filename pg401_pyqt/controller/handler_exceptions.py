
import requests
from pg401_pyqt.utils.logger import logger

def handler_exceptions(e):
    if isinstance(e, requests.exceptions.ConnectionError):
        logger.error(f"A Connection error occurred. {e}")
    elif isinstance(e, requests.exceptions.HTTPError):
        logger.error(f"An HTTP error occurred. {e}")
    elif isinstance(e, requests.exceptions.Timeout):
        logger.error(f"The request timed out. {e}")
    elif isinstance(e, requests.exceptions.RequestException):
        logger.error(f"Another exception occurred {e}")


def validate_wave_params(range_init_nm: float, range_end_nm: float, step_nm: float, time_s: float):
    """
    Valida los parámetros de entrada para las funciones de barrido de longitud de onda.
    Lanza ValueError si algún parámetro está fuera de rango.
    """
    if not (210 <= range_init_nm <= 2300):
        raise ValueError(f"Longitud de onda inicial fuera de rango: {range_init_nm} nm (debe estar entre 210 y 2300)")
    if not (210 <= range_end_nm <= 2300):
        raise ValueError(f"Longitud de onda final fuera de rango: {range_end_nm} nm (debe estar entre 210 y 2300)")
    if not (0.1 <= step_nm <= 50):
        raise ValueError(f"Step fuera de rango: {step_nm} nm (debe estar entre 0.1 y 50)")
    if not (0.1 <= time_s <= 30):
        raise ValueError(f"Tiempo de espera fuera de rango: {time_s} s (debe estar entre 0.1 y 30)")