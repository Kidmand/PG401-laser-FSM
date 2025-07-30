def parse_list_response(response: str):
    if response is None:
        return []
    return response.split("<br>")

def parse_exe_response(response: str):
    if response is None:
        return []
    return response.split("<br>")

def parse_rdvar_response(response: str):
    if response is None:
        return []
    return response.split("<br>")

def parse_data_response(response: str):
    if response is None:
        return []
    return response.split("<br>")

def parse_ces_response(response: str):
    if response is None:
        return []
    return response.split("<br>")



