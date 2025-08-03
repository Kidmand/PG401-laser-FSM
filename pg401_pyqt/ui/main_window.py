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
from PyQt6.QtCore import Qt
from pg401_pyqt.controller.laser_api import list_command
from pg401_pyqt.controller.enums_commands import List
from pg401_pyqt.controller.laser_api import exe_wave_command, Exe


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
            QPushButton#estado { background-color: #1976d2; color: white; }
            QTextEdit { background: #181a20; color: #e0e0e0; font-size: 13px; border-radius: 6px; }
        """)

        # Solo widgets y layouts originales, sin tooltips ni validación ni botones extra


        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(24, 18, 24, 18)

        # Sección de estado (solo label para mostrar valor actual)
        estado_group = QGroupBox("Estado del sistema")
        estado_layout = QVBoxLayout()
        estado_layout.setSpacing(10)
        estado_layout.setContentsMargins(10, 10, 10, 10)
        label_estado_title = QLabel("Estado del láser:")
        label_estado_title.setFont(QFont("Arial", 13))
        self.label_estado = QLabel("Desconocido")
        self.label_estado.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        estado_row = QHBoxLayout()
        estado_row.addWidget(label_estado_title)
        estado_row.addWidget(self.label_estado)
        estado_row.addStretch()
        estado_layout.addLayout(estado_row)
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
        self.input_step.setPlaceholderText("Step (nm)")
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
        self.btn_estado = QPushButton("Consultar Estado Actual")
        self.btn_estado.setObjectName("estado")
        self.btn_estado.setMinimumHeight(38)
        btn_layout.addWidget(self.btn_barrido)
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

        # Conectar señales
        self.btn_barrido.clicked.connect(self.iniciar_barrido)
        self.btn_estado.clicked.connect(self.consultar_estado)

    def _append_log(self, html):
        # Solo append y scroll, sin contador ni separación especial
        self.text_log.append(html)
        from PyQt6.QtGui import QTextCursor
        self.text_log.moveCursor(QTextCursor.MoveOperation.End)

    def consultar_estado(self):
        # Consulta real a la URL del MaxiOPG y muestra la respuesta completa en el log
        from pg401_pyqt.controller.laser_api import wave_command
        try:
            respuesta = wave_command()
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
                self.label_estado.setText(f"{valor} nm")
            else:
                self.label_estado.setText("Respuesta recibida")
        except Exception as e:
            self._append_log(f"<span style='color:red;'>Error al consultar MaxiOPG: {e}</span>")

    def iniciar_barrido(self):
        try:
            range_init_nm = float(self.input_init.text())
            range_end_nm = float(self.input_end.text())
            step_nm = float(self.input_step.text())
            time_s = float(self.input_time.text())
        except Exception:
            self._append_log("<span style='color:red;'>Ingrese todos los parámetros numéricos correctamente.</span>")
            return

        self._append_log("<b>Iniciando barrido...</b>")
        try:
            barrido_info = exe_wave_command(Exe.WAVELENGTH, range_init_nm, range_end_nm, step_nm, time_s)
        except Exception as e:
            self._append_log(f"<span style='color:red;'>Error general: {e}</span>")
            return
        self._append_log("<b>Resultado del barrido:</b>")
        for info in barrido_info:
            self._append_log("<pre>" + info + "</pre>")
