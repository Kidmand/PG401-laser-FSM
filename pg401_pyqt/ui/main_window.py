from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel, 
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QWidget,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from pg401_pyqt.controller.laser_api import list_command
from pg401_pyqt.controller.enums_commands import List
from pg401_pyqt.controller.laser_api import exe_wave_command, Exe


class BarridoThread(QThread):
    # Señales para comunicarse con la interfaz
    mensaje_signal = pyqtSignal(str)  # Para enviar mensajes al log
    progreso_signal = pyqtSignal(float)  # Para reportar el progreso
    terminado_signal = pyqtSignal(bool)  # Para indicar si terminó exitosamente
    
    def __init__(self, query, range_init_nm, range_end_nm, step_nm, time_s):
        super().__init__()
        self.query = query
        self.range_init_nm = range_init_nm
        self.range_end_nm = range_end_nm
        self.step_nm = step_nm
        self.time_s = time_s
        self.stop_requested = False
        self.ultimo_valor_procesado = range_init_nm
        
    def stop(self):
        """Solicita detener el hilo"""
        self.stop_requested = True
        
    def run(self):
        """Ejecuta el barrido en un hilo separado con manejo seguro de errores"""
        try:
            from pg401_pyqt.controller.laser_api import logic_wave_forward, logic_wave_backward
            from pg401_pyqt.controller.handler_exceptions import validate_wave_params
            
            # Validar parámetros
            validate_wave_params(self.range_init_nm, self.range_end_nm, self.step_nm, self.time_s)
            
            # Verificar stop antes de empezar
            if self.stop_requested:
                self.terminado_signal.emit(False)
                return
            
            # Determinar dirección del barrido
            if self.range_end_nm >= self.range_init_nm:
                info = logic_wave_forward(self.query, self.range_init_nm, self.range_end_nm, 
                                        self.step_nm, self.time_s, self)
            else:
                info = logic_wave_backward(self.query, self.range_init_nm, self.range_end_nm, 
                                         self.step_nm, self.time_s, self)
            
            # Enviar resultados solo si no se solicitó stop
            if not self.stop_requested:
                for mensaje in info:
                    if self.stop_requested:
                        break
                    self.mensaje_signal.emit(mensaje)
            
            # Señal de terminación
            self.terminado_signal.emit(not self.stop_requested)
            
        except Exception as e:
            self.mensaje_signal.emit(f"<span style='color:red;'>Error en el barrido: {e}</span>")
            self.terminado_signal.emit(False)


class MainWindow(QMainWindow):
    # Métodos extra eliminados, solo funcionalidad original
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PG401 - Control Láser")
        self.setGeometry(200, 200, 750, 480)
        self.setStyleSheet("""
            QMainWindow { background-color: #23272e; }
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                background: #2d323b;
                border-radius: 12px;
                color: #e0e0e0;
                padding: 18px 18px 18px 18px;
                margin-top: 32px;
                margin-bottom: 32px;
                box-shadow: 0 4px 24px 0 rgba(0,0,0,0.18);
                border: 1.5px solid #23272e;
            }
            QLabel { color: #e0e0e0; }
            QLineEdit { background: #23272e; color: #e0e0e0; border: 1px solid #444; border-radius: 4px; padding: 4px; }
            QPushButton { font-size: 14px; padding: 8px 18px; border-radius: 6px; }
            QPushButton#barrido { background-color: #388e3c; color: white; }
            QPushButton#continuar { background-color: #ff9800; color: white; }
            QPushButton#continuar:disabled { background-color: #666; color: #999; }
            QPushButton#stop { background-color: #d32f2f; color: white; }
            QPushButton#stop:disabled { background-color: #666; color: #999; }
            QPushButton#estado { background-color: #1976d2; color: white; }
            QTextEdit { background: #181a20; color: #e0e0e0; font-size: 13px; border-radius: 6px; }
        """)

        # Solo widgets y layouts originales, sin tooltips ni validación ni botones extra


        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(24, 18, 24, 18)

        # Sección de estado (mejorada con más información)
        estado_group = QGroupBox("Estado del Láser PG401")
        estado_layout = QVBoxLayout()
        estado_layout.setSpacing(10)
        estado_layout.setContentsMargins(10, 10, 10, 10)
        
        # Primera fila: Longitud de onda actual
        estado_row1 = QHBoxLayout()
        label_longitud_title = QLabel("Longitud de onda actual:")
        label_longitud_title.setFont(QFont("Arial", 13))
        self.label_estado = QLabel("Presiona 'Consultar Estado' para actualizar")
        self.label_estado.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_estado.setStyleSheet("color: #90caf9;")  # Azul claro por defecto
        estado_row1.addWidget(label_longitud_title)
        estado_row1.addWidget(self.label_estado)
        estado_row1.addStretch()
        
        # Segunda fila: Información de rango válido
        estado_row2 = QHBoxLayout()
        label_rango = QLabel("Rango válido:")
        label_rango.setFont(QFont("Arial", 11))
        label_rango_valor = QLabel("210.0000 - 2300.0000 nm")
        label_rango_valor.setFont(QFont("Arial", 11))
        label_rango_valor.setStyleSheet("color: #90caf9;")
        estado_row2.addWidget(label_rango)
        estado_row2.addWidget(label_rango_valor)
        estado_row2.addStretch()
        
        # Tercera fila: Estado de conexión
        estado_row3 = QHBoxLayout()
        label_conexion_title = QLabel("Estado conexión:")
        label_conexion_title.setFont(QFont("Arial", 11))
        self.label_conexion = QLabel("No verificado")
        self.label_conexion.setFont(QFont("Arial", 11))
        self.label_conexion.setStyleSheet("color: #ffb74d;")  # Amarillo por defecto (no verificado)
        estado_row3.addWidget(label_conexion_title)
        estado_row3.addWidget(self.label_conexion)
        estado_row3.addStretch()
        
        estado_layout.addLayout(estado_row1)
        estado_layout.addLayout(estado_row2)
        estado_layout.addLayout(estado_row3)
        estado_group.setLayout(estado_layout)
        main_layout.addWidget(estado_group)
        # Separador visual
        main_layout.addSpacing(8)

        # Sección de parámetros de barrido
        sweep_group = QGroupBox("Parámetros de Barrido")
        sweep_layout = QVBoxLayout()
        sweep_layout.setSpacing(10)
        sweep_layout.setContentsMargins(10, 10, 10, 10)
        from PyQt6.QtWidgets import QLineEdit
        grid = QHBoxLayout()
        grid.setSpacing(8)  # Espacio entre pares
        pair_spacing = 1  # Espacio mínimo entre etiqueta y campo
        self.input_init = QLineEdit()
        self.input_init.setPlaceholderText("Inicial (nm)")
        self.input_init.setFixedWidth(90)
        self.input_end = QLineEdit()
        self.input_end.setPlaceholderText("Final (nm)")
        self.input_end.setFixedWidth(90)
        self.input_step = QLineEdit()
        self.input_step.setPlaceholderText("0.01")  # Valor sugerido de 0.01 nm
        self.input_step.setText("0.01")  # Valor por defecto
        self.input_step.setFixedWidth(90)
        self.input_time = QLineEdit()
        self.input_time.setPlaceholderText("Tiempo (s)")
        self.input_time.setFixedWidth(90)
        for widget in [self.input_init, self.input_end, self.input_step, self.input_time]:
            widget.setFont(QFont("Arial", 12))
        label_inicio = QLabel("Inicio:")
        label_fin = QLabel("Fin:")
        label_step = QLabel("Step:")
        label_tiempo = QLabel("Tiempo:")
        for label in [label_inicio, label_fin, label_step, label_tiempo]:
            label.setFont(QFont("Arial", 12))
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Pares etiqueta-campo, bien juntos
        grid.addWidget(label_inicio)
        grid.addSpacing(pair_spacing)
        grid.addWidget(self.input_init)
        grid.addSpacing(10)
        grid.addWidget(label_fin)
        grid.addSpacing(pair_spacing)
        grid.addWidget(self.input_end)
        grid.addSpacing(10)
        grid.addWidget(label_step)
        grid.addSpacing(pair_spacing)
        grid.addWidget(self.input_step)
        grid.addSpacing(10)
        grid.addWidget(label_tiempo)
        grid.addSpacing(pair_spacing)
        grid.addWidget(self.input_time)
        sweep_layout.addLayout(grid)
        
        # Sección para modificar step cuando está detenido
        modificar_layout = QHBoxLayout()
        modificar_layout.setSpacing(8)
        self.label_nuevo_step = QLabel("Nuevo Step para continuar:")
        self.label_nuevo_step.setFont(QFont("Arial", 11))
        self.input_nuevo_step = QLineEdit()
        self.input_nuevo_step.setPlaceholderText("0.01")
        self.input_nuevo_step.setText("0.01")
        self.input_nuevo_step.setFixedWidth(90)
        self.input_nuevo_step.setFont(QFont("Arial", 12))
        self.btn_aplicar_step = QPushButton("Aplicar Nuevo Step")
        self.btn_aplicar_step.setObjectName("aplicar")
        self.btn_aplicar_step.setEnabled(False)
        self.btn_aplicar_step.setStyleSheet("QPushButton#aplicar { background-color: #9c27b0; color: white; }")
        
        modificar_layout.addWidget(self.label_nuevo_step)
        modificar_layout.addWidget(self.input_nuevo_step)
        modificar_layout.addWidget(self.btn_aplicar_step)
        modificar_layout.addStretch()
        sweep_layout.addLayout(modificar_layout)
        
        sweep_group.setLayout(sweep_layout)
        main_layout.addWidget(sweep_group)
        # Separador visual
        main_layout.addSpacing(8)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_barrido = QPushButton("Iniciar Barrido")
        self.btn_barrido.setObjectName("barrido")
        self.btn_barrido.setMinimumHeight(38)
        self.btn_continuar = QPushButton("Continuar Barrido")
        self.btn_continuar.setObjectName("continuar")
        self.btn_continuar.setMinimumHeight(38)
        self.btn_continuar.setEnabled(False)  # Deshabilitado inicialmente
        self.btn_stop = QPushButton("Detener Barrido")
        self.btn_stop.setObjectName("stop")
        self.btn_stop.setMinimumHeight(38)
        self.btn_stop.setEnabled(False)  # Deshabilitado inicialmente
        self.btn_estado = QPushButton("Consultar Estado Actual")
        self.btn_estado.setObjectName("estado")
        self.btn_estado.setMinimumHeight(38)
        btn_layout.addWidget(self.btn_barrido)
        btn_layout.addWidget(self.btn_continuar)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_estado)
        main_layout.addLayout(btn_layout)
        # Separador visual
        main_layout.addSpacing(8)


        # Sección de logs/mensajes
        log_group = QGroupBox("Mensajes y logs")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(10, 10, 10, 10)
        log_layout.setSpacing(0)
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMinimumHeight(180)
        self.text_log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Layout horizontal para log y botón limpiar
        log_row = QHBoxLayout()
        log_row.addWidget(self.text_log)
        # Solo el QTextEdit para el log, sin botones ni contador
        log_layout.addLayout(log_row)
        log_group.setLayout(log_layout)
        # El log ocupa todo el espacio restante
        main_layout.addWidget(log_group, stretch=1)

        # Contenedor central
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Variable de control para detener el barrido
        self.stop_barrido = False
        self.barrido_thread = None  # Referencia al hilo del barrido
        
        # Variables para continuar el barrido
        self.ultimo_barrido = {
            'range_init_nm': None,
            'range_end_nm': None,
            'step_nm': None,
            'time_s': None,
            'ultimo_valor': None,
            'completado': True
        }

        # Conectar señales
        self.btn_barrido.clicked.connect(self.iniciar_barrido)
        self.btn_continuar.clicked.connect(self.continuar_barrido)
        self.btn_stop.clicked.connect(self.detener_barrido)
        self.btn_estado.clicked.connect(self.consultar_estado)
        self.btn_aplicar_step.clicked.connect(self.aplicar_nuevo_step)
        
        # Timer para actualización automática del estado
        self.timer_estado = QTimer()
        self.timer_estado.timeout.connect(self.actualizar_estado_automatico)
        self.consulta_automatica_activa = False
        
        # Variable para rastrear el estado de conexión
        self._conexion_perdida = False
        
        # Consultar estado inicial al arrancar la aplicación
        self.consultar_estado_inicial()

    def aplicar_nuevo_step(self):
        """Aplica un nuevo step para continuar el barrido"""
        try:
            nuevo_step = float(self.input_nuevo_step.text())
            if nuevo_step <= 0:
                self._append_log("<span style='color:red;'>El step debe ser un valor positivo.</span>")
                return
                
            # Actualizar el step en los parámetros del último barrido
            self.ultimo_barrido['step_nm'] = nuevo_step
            self._append_log(f"<span style='color:#9c27b0;'>Nuevo step aplicado: <b>{nuevo_step:.4f} nm</b></span>")
            
            # Actualizar también el campo principal para consistencia
            self.input_step.setText(str(nuevo_step))
            
        except ValueError:
            self._append_log("<span style='color:red;'>Ingrese un valor numérico válido para el step.</span>")

    def actualizar_estado_automatico(self):
        """Actualiza el estado automáticamente sin mostrar logs completos"""
        from pg401_pyqt.controller.laser_api import wave_command
        try:
            respuesta = wave_command()
            if respuesta:
                valor = None
                for line in respuesta.splitlines():
                    if line.strip().startswith('Value:'):
                        try:
                            valor = float(line.split(':')[1].split()[0])
                        except Exception:
                            pass
                        break
                        
                if valor is not None:
                    # Si estaba desconectado, mostrar mensaje de reconexión
                    if hasattr(self, '_conexion_perdida') and self._conexion_perdida:
                        self._append_log("<span style='color:#4caf50;'><b>Conexión restablecida con el servidor</b></span>")
                        self._conexion_perdida = False
                    
                    self.label_estado.setText(f"{valor:.4f} nm")
                    self.label_estado.setStyleSheet("color: #4caf50; font-weight: bold;")  # Verde para valor válido
                    self.label_conexion.setText("Conectado")
                    self.label_conexion.setStyleSheet("color: #4caf50; font-weight: bold;")  # Verde para conectado
                else:
                    self.label_estado.setText("Valor no encontrado")
                    self.label_estado.setStyleSheet("color: #ff9800; font-weight: bold;")  # Naranja para advertencia
                    self.label_conexion.setText("Respuesta incompleta")
                    self.label_conexion.setStyleSheet("color: #ff9800; font-weight: bold;")  # Naranja para advertencia
            else:
                # Detectar desconexión
                if not hasattr(self, '_conexion_perdida') or not self._conexion_perdida:
                    self._append_log("<span style='color:#f44336;'><b>Servidor desconectado - Sin respuesta del láser</b></span>")
                    self._conexion_perdida = True
                
                self.label_estado.setText("Sin conexión")
                self.label_estado.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
                self.label_conexion.setText("Desconectado")
                self.label_conexion.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para sin conexión
                
        except Exception as e:
            # Detectar error de comunicación
            if not hasattr(self, '_conexion_perdida') or not self._conexion_perdida:
                self._append_log(f"<span style='color:#f44336;'><b>Error de comunicación: {e}</b></span>")
                self._conexion_perdida = True
            
            self.label_estado.setText("Error de conexión")
            self.label_estado.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
            self.label_conexion.setText("Error de comunicación")
            self.label_conexion.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error

    def consultar_estado_inicial(self):
        """Consulta el estado inicial sin mostrar logs"""
        from pg401_pyqt.controller.laser_api import wave_command
        try:
            respuesta = wave_command()
            if respuesta:
                valor = None
                for line in respuesta.splitlines():
                    if line.strip().startswith('Value:'):
                        try:
                            valor = float(line.split(':')[1].split()[0])
                        except Exception:
                            pass
                        break
                        
                if valor is not None:
                    self.label_estado.setText(f"{valor:.4f} nm")
                    self.label_estado.setStyleSheet("color: #4caf50; font-weight: bold;")  # Verde para valor válido
                    self.label_conexion.setText("Conectado")
                    self.label_conexion.setStyleSheet("color: #4caf50; font-weight: bold;")  # Verde para conectado
                    self._conexion_perdida = False  # Marcar como conectado
                else:
                    self.label_estado.setText("Valor no encontrado")
                    self.label_estado.setStyleSheet("color: #ff9800; font-weight: bold;")  # Naranja para advertencia
                    self.label_conexion.setText("Respuesta incompleta")
                    self.label_conexion.setStyleSheet("color: #ff9800; font-weight: bold;")  # Naranja para advertencia
            else:
                self.label_estado.setText("Sin conexión")
                self.label_estado.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
                self.label_conexion.setText("Desconectado")
                self.label_conexion.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para sin conexión
                self._conexion_perdida = True  # Marcar como desconectado
                
        except Exception:
            self.label_estado.setText("Error de conexión")
            self.label_estado.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
            self.label_conexion.setText("Error de comunicación")
            self.label_conexion.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
            self._conexion_perdida = True  # Marcar como desconectado

    def _append_log(self, html):
        # Solo append y scroll, sin contador ni separación especial
        self.text_log.append(html)
        from PyQt6.QtGui import QTextCursor
        self.text_log.moveCursor(QTextCursor.MoveOperation.End)

    def continuar_barrido(self):
        """Continúa el barrido desde donde se quedó de forma segura"""
        try:
            if self.ultimo_barrido['completado']:
                self._append_log("<span style='color:#ff9800;'>No hay barrido pendiente para continuar.</span>")
                return
                
            if self.ultimo_barrido['ultimo_valor'] is None:
                self._append_log("<span style='color:red;'>No se puede continuar: no hay punto de inicio válido.</span>")
                return
            
            # Calcular nuevo punto de inicio
            if self.ultimo_barrido['range_end_nm'] >= self.ultimo_barrido['range_init_nm']:
                # Barrido hacia adelante
                nuevo_inicio = self.ultimo_barrido['ultimo_valor'] + self.ultimo_barrido['step_nm']
                if nuevo_inicio > self.ultimo_barrido['range_end_nm']:
                    self._append_log("<span style='color:#4caf50;'>El barrido ya estaba completado.</span>")
                    self.ultimo_barrido['completado'] = True
                    self.btn_continuar.setEnabled(False)
                    return
            else:
                # Barrido hacia atrás
                nuevo_inicio = self.ultimo_barrido['ultimo_valor'] - self.ultimo_barrido['step_nm']
                if nuevo_inicio < self.ultimo_barrido['range_end_nm']:
                    self._append_log("<span style='color:#4caf50;'>El barrido ya estaba completado.</span>")
                    self.ultimo_barrido['completado'] = True
                    self.btn_continuar.setEnabled(False)
                    return
            
            # Configurar estado de botones
            self.stop_barrido = False
            self.btn_barrido.setEnabled(False)
            self.btn_continuar.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.btn_aplicar_step.setEnabled(False)  # Deshabilitar mientras corre

            self._append_log(f"<b>Continuando barrido desde {nuevo_inicio:.4f} nm con step {self.ultimo_barrido['step_nm']:.4f} nm...</b>")
            
            # Crear y configurar el hilo del barrido
            self.barrido_thread = BarridoThread(
                Exe.WAVELENGTH, 
                nuevo_inicio, 
                self.ultimo_barrido['range_end_nm'], 
                self.ultimo_barrido['step_nm'], 
                self.ultimo_barrido['time_s']
            )
            
            # Actualizar los parámetros para el próximo continue
            self.ultimo_barrido['range_init_nm'] = nuevo_inicio
            
            # Conectar señales del hilo
            self.barrido_thread.mensaje_signal.connect(self._append_log)
            self.barrido_thread.terminado_signal.connect(self._on_barrido_terminado)
            
            # Iniciar el hilo
            self.barrido_thread.start()
            
        except Exception as e:
            self._append_log(f"<span style='color:red;'>Error al continuar barrido: {e}</span>")
            # Restaurar estado de botones en caso de error
            self.btn_barrido.setEnabled(True)
            self.btn_stop.setEnabled(False)
            if not self.ultimo_barrido.get('completado', True):
                self.btn_aplicar_step.setEnabled(True)

    def detener_barrido(self):
        """Detiene el barrido en ejecución de forma segura"""
        try:
            if self.barrido_thread and self.barrido_thread.isRunning():
                self._append_log("<span style='color:#ff9800;'><b>Solicitando detener barrido...</b></span>")
                self.barrido_thread.stop()
                
                # Esperar a que el hilo termine de forma segura (máximo 3 segundos)
                if not self.barrido_thread.wait(3000):  # 3000ms = 3 segundos
                    self._append_log("<span style='color:red;'><b>Forzando terminación del barrido...</b></span>")
                    self.barrido_thread.terminate()
                    self.barrido_thread.wait()  # Esperar terminación forzada
                
                self._append_log("<span style='color:#ff9800;'><b>Barrido detenido correctamente.</b></span>")
            else:
                self.stop_barrido = True
                self._append_log("<span style='color:#ff9800;'><b>Barrido detenido.</b></span>")
                
            # Restaurar estado de botones de forma segura
            self.btn_stop.setEnabled(False)
            self.btn_barrido.setEnabled(True)
            
            # Habilitar continuar solo si hay un barrido incompleto
            if not self.ultimo_barrido.get('completado', True):
                self.btn_continuar.setEnabled(True)
                # Habilitar la modificación del step cuando está detenido
                self.btn_aplicar_step.setEnabled(True)
                self._append_log("<span style='color:#9c27b0;'>Puedes modificar el step y continuar el barrido</span>")
            else:
                self.btn_aplicar_step.setEnabled(False)
                
        except Exception as e:
            self._append_log(f"<span style='color:red;'>Error al detener barrido: {e}</span>")
            # En caso de error, restaurar botones de forma segura
            self.btn_stop.setEnabled(False)
            self.btn_barrido.setEnabled(True)
            self.btn_aplicar_step.setEnabled(False)

    def consultar_estado(self):
        # Consulta real a la URL del MaxiOPG y muestra la respuesta completa en el log
        from pg401_pyqt.controller.laser_api import wave_command
        try:
            respuesta = wave_command()
            if respuesta:
                self._append_log(f"<pre><span style='color:#00ff00;'>[STATE] {respuesta}</span></pre>")
                valor = None
                for line in respuesta.splitlines():
                    if line.strip().startswith('Value:'):
                        try:
                            valor = float(line.split(':')[1].split()[0])
                        except Exception:
                            pass
                        break
                        
                if valor is not None:
                    # Si estaba desconectado, mostrar mensaje de reconexión
                    if hasattr(self, '_conexion_perdida') and self._conexion_perdida:
                        self._append_log("<span style='color:#4caf50;'><b>Conexión restablecida con el servidor</b></span>")
                        self._conexion_perdida = False
                    
                    self.label_estado.setText(f"{valor:.4f} nm")
                    self.label_estado.setStyleSheet("color: #4caf50; font-weight: bold;")  # Verde para valor válido
                    self.label_conexion.setText("Conectado")
                    self.label_conexion.setStyleSheet("color: #4caf50; font-weight: bold;")  # Verde para conectado
                    self._append_log(f"<span style='color:#4caf50;'>Longitud actual del láser: <b>{valor:.4f} nm</b></span>")
                    
                    # Activar actualización automática en tiempo real
                    if not self.consulta_automatica_activa:
                        self.consulta_automatica_activa = True
                        self.timer_estado.start(2000)  # Actualizar cada 2 segundos
                        self._append_log("<span style='color:#2196f3;'>Actualización automática del estado activada (cada 2s)</span>")
                    
                else:
                    self.label_estado.setText("Valor no encontrado")
                    self.label_estado.setStyleSheet("color: #ff9800; font-weight: bold;")  # Naranja para advertencia
                    self.label_conexion.setText("Respuesta incompleta")
                    self.label_conexion.setStyleSheet("color: #ff9800; font-weight: bold;")  # Naranja para advertencia
                    self._append_log("<span style='color:#ff9800;'>No se pudo extraer el valor de longitud de onda</span>")
            else:
                # Detectar desconexión en consulta manual
                if not hasattr(self, '_conexion_perdida') or not self._conexion_perdida:
                    self._append_log("<span style='color:#f44336;'><b>Servidor desconectado - Sin respuesta del láser</b></span>")
                    self._conexion_perdida = True
                
                self.label_estado.setText("Sin respuesta")
                self.label_estado.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
                self.label_conexion.setText("Desconectado")
                self.label_conexion.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para sin conexión
                self._append_log("<span style='color:red;'>No se recibió respuesta del servidor</span>")
                
        except Exception as e:
            # Detectar error de comunicación en consulta manual
            if not hasattr(self, '_conexion_perdida') or not self._conexion_perdida:
                self._append_log(f"<span style='color:#f44336;'><b>Error de comunicación: {e}</b></span>")
                self._conexion_perdida = True
            
            self.label_estado.setText("Error de conexión")
            self.label_estado.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
            self.label_conexion.setText("Error de comunicación")
            self.label_conexion.setStyleSheet("color: #f44336; font-weight: bold;")  # Rojo para error
            self._append_log(f"<span style='color:red;'>Error al consultar estado del láser: {e}</span>")

    def iniciar_barrido(self):
        # Validar entrada
        try:
            range_init_nm = float(self.input_init.text())
            range_end_nm = float(self.input_end.text())
            step_nm = float(self.input_step.text())
            time_s = float(self.input_time.text())
        except Exception:
            self._append_log("<span style='color:red;'>Ingrese todos los parámetros numéricos correctamente.</span>")
            return

        # Validación adicional para evitar saturar el servidor
        if step_nm <= 0.01 and time_s < 0.1:
            self._append_log("<span style='color:#ff9800;'><b>ADVERTENCIA:</b> Para steps ≤ 0.01 nm se recomienda tiempo ≥ 0.1s para evitar saturar el servidor.</span>")

        # Calcular número total de steps para informar al usuario
        if range_end_nm != range_init_nm:
            total_steps = abs((range_end_nm - range_init_nm) / step_nm) + 1
            tiempo_estimado = total_steps * time_s
            
            # Advertencia especial para barridos muy largos
            if total_steps > 1000:
                self._append_log(f"<span style='color:#ff9800;'><b>BARRIDO EXTENSO:</b> {int(total_steps)} pasos, duración estimada: {tiempo_estimado/60:.1f} minutos</span>")
            else:
                self._append_log(f"<span style='color:#2196f3;'>Barrido estimado: {int(total_steps)} pasos, duración aprox: {tiempo_estimado:.1f}s</span>")

        # Guardar parámetros para posible continuación
        self.ultimo_barrido = {
            'range_init_nm': range_init_nm,
            'range_end_nm': range_end_nm,
            'step_nm': step_nm,
            'time_s': time_s,
            'ultimo_valor': range_init_nm,
            'completado': False
        }

        # Configurar estado de botones para el barrido
        self.stop_barrido = False
        self.btn_barrido.setEnabled(False)
        self.btn_continuar.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_aplicar_step.setEnabled(False)  # Deshabilitar durante el barrido

        self._append_log("<b>Iniciando barrido...</b>")
        
        # Crear y configurar el hilo del barrido
        self.barrido_thread = BarridoThread(Exe.WAVELENGTH, range_init_nm, range_end_nm, step_nm, time_s)
        
        # Conectar señales del hilo
        self.barrido_thread.mensaje_signal.connect(self._append_log)
        self.barrido_thread.terminado_signal.connect(self._on_barrido_terminado)
        
        # Iniciar el hilo
        self.barrido_thread.start()
    
    def _on_barrido_terminado(self, exitoso):
        """Maneja la finalización del barrido de forma segura"""
        try:
            # Restaurar estado de botones de forma segura
            self.btn_barrido.setEnabled(True)
            self.btn_stop.setEnabled(False)
            
            if exitoso:
                self._append_log("<span style='color:#4caf50;'><b>Barrido completado exitosamente.</b></span>")
                self.ultimo_barrido['completado'] = True
                self.btn_continuar.setEnabled(False)
                self.btn_aplicar_step.setEnabled(False)
            else:
                self._append_log("<span style='color:#ff9800;'><b>Barrido detenido por el usuario.</b></span>")
                # Si fue detenido, obtener el último valor del hilo si es posible
                if self.barrido_thread and hasattr(self.barrido_thread, 'ultimo_valor_procesado'):
                    self.ultimo_barrido['ultimo_valor'] = self.barrido_thread.ultimo_valor_procesado
                    self._append_log(f"<span style='color:#2196f3;'>Última posición procesada: {self.ultimo_barrido['ultimo_valor']:.4f} nm</span>")
                self.ultimo_barrido['completado'] = False
                self.btn_continuar.setEnabled(True)
                self.btn_aplicar_step.setEnabled(True)  # Permitir cambiar step
            
            # Limpiar referencia del hilo de forma segura
            if self.barrido_thread:
                self.barrido_thread.deleteLater()  # Eliminar de forma segura en PyQt
                self.barrido_thread = None
                
        except Exception as e:
            self._append_log(f"<span style='color:red;'>Error al finalizar barrido: {e}</span>")
            # Restaurar estado mínimo en caso de error
            self.btn_barrido.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.btn_aplicar_step.setEnabled(False)
            self.barrido_thread = None
