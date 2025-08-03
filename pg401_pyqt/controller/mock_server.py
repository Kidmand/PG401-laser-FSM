from flask import Flask, request
app = Flask(__name__)

# Estado simulado de longitud de onda
current_wavelength = {'value': 500.1}

@app.route('/REST/HTTP_CMD/', methods=['GET'])
def mock_set_wavelength():
    # Simula el seteo de longitud de onda por query string
    args = request.query_string.decode()
    import re
    match = re.search(r'SetWaveLengthPG401/(\d+\.?\d*)', args)
    if match:
        wl = float(match.group(1))
        current_wavelength['value'] = wl
        return f"OK: Longitud de onda seteada a {wl} nm"
    return "OK: Comando recibido"

@app.route('/MaxiOPG/33/WaveLength', methods=['GET'])
def mock_wave_status():
    # Simula la respuesta de estado del láser
    return f"""Device: MaxiOPG:33
Register: WaveLength
Min_value: 210
Max_value: 2300
RW: yes
NV: yes
Formato: %.7gnm
Error: (0) Success, no error
Value: {current_wavelength['value'] if current_wavelength['value'] is not None else 0.0}
"""

if __name__ == '__main__':
    app.run(host='192.168.1.11', port=8081)



