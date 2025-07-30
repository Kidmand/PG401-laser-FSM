import requests
from pg401_pyqt.controller.enums_commands import List, Exe, Rdvar
from pg401_pyqt.controller.handler_exceptions import handler_exeptions
from pg401_pyqt.controller.response_handler import parse_ces_response

IP = "192.168.0.160"
LAN_IP = "192.254.224.164"
IP_MOCK = "localhost"
URL_BASE = f"http://{LAN_IP}:8081/REST/HTTP_CMD/?"

def list_command(query: List, time: float=None):
    try:
        if(query == List.CLOG_WHERE):
            response = requests.get(URL_BASE + query.value + str(time))
        else:
            response = requests.get(URL_BASE + query.value)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exeptions(e)


def exe_command(query: Exe, aplification: int=None):
    try:
        if (query == Exe.AMPLIFICATION):
            response = requests.get(URL_BASE + query.value + str(aplification))
        else:
            response = requests.get(URL_BASE + query.value)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exeptions(e)


def rdvar_command(query: Rdvar):
    try:
        response = requests.get(URL_BASE + query.value) 
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exeptions(e)


def data_command(channelNo: int, time: float=None):
    try:
        if (time is not None):
            response = requests.get(URL_BASE + "DATA/" + str(channelNo) + "/" + str(time))
        else:
            response = requests.get(URL_BASE + "DATA/" + str(channelNo))
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exeptions(e)


def ces_command(time: float=None):
    try:
        if (time is not None):
            response = requests.get(URL_BASE + "CES/" + str(time))
        else:
            response = requests.get(URL_BASE + "CES")
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        handler_exeptions(e)

response = ces_command()
print("Esto es lo que está en la respuesta:", response)
response_parse = parse_ces_response(response)
print("Esta es la respuesta parseada:", response_parse)

