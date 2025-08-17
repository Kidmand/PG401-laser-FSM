from flask import Flask, request
from datetime import datetime
app = Flask(__name__)

# Estado simulado de longitud de onda
current_wavelength = {'value': 500.1, 'last_updated': datetime.now()}

@app.route('/REST/HTTP_CMD/', methods=['GET'])
def mock_set_wavelength():
    # Simula el seteo de longitud de onda por query string
    args = request.query_string.decode()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Comando recibido: {args}")
    
    import re
    match = re.search(r'SetWavelengthPG401/(\d+\.?\d*)', args)
    if match:
        wl = float(match.group(1))
        current_wavelength['value'] = wl
        current_wavelength['last_updated'] = datetime.now()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Longitud de onda actualizada: {wl} nm")
        return f"OK: Longitud de onda seteada a {wl} nm"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Comando no reconocido")
    return "OK: Comando recibido"

@app.route('/MaxiOPG/33/WaveLength', methods=['GET'])
def mock_wave_status():
    # Simula la respuesta de estado del láser
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Consulta de estado - Longitud actual: {current_wavelength['value']} nm")
    
    return f"""Device: MaxiOPG:33
Register: WaveLength
Min_value: 210
Max_value: 2300
RW: yes
NV: yes
Formato: %.7gnm
Error: (0) Success, no error
Value: {current_wavelength['value'] if current_wavelength['value'] is not None else 0.0}
Last_Updated: {current_wavelength['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}
Status: Mock Server - Funcionando correctamente

"""

@app.route('/', methods=['GET'])
def mock_status():
    """Endpoint para ver el estado actual del mock server"""
    return f"""
    <h1>Mock Server PG401 - Estado Actual</h1>
    <h2>Información del Láser:</h2>
    <ul>
        <li><strong>Longitud de Onda Actual:</strong> {current_wavelength['value']} nm</li>
        <li><strong>Última Actualización:</strong> {current_wavelength['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}</li>
        <li><strong>Rango Válido:</strong> 210 - 2300 nm</li>
        <li><strong>Estado:</strong> Activo</li>
    </ul>
    <h2>Endpoints Disponibles:</h2>
    <ul>
        <li><code>/REST/HTTP_CMD/?EXE/SetWavelengthPG401/[valor]</code> - Establecer longitud de onda</li>
        <li><code>/MaxiOPG/33/WaveLength</code> - Consultar estado actual</li>
    </ul>
    <p><em>Servidor corriendo en puerto 8080</em></p>
    """

if __name__ == '__main__':
    print("Iniciando Mock Server PG401...")
    print(f"Estado inicial: {current_wavelength['value']} nm")
    print("Accede a http://localhost:8080 para ver el estado")
    print("Endpoints:")
    print("   - GET /REST/HTTP_CMD/?EXE/SetWavelengthPG401/[valor]")
    print("   - GET /MaxiOPG/33/WaveLength")
    print("   - GET / (estado del servidor)")
    app.run(host='0.0.0.0', port=8080, debug=True)



