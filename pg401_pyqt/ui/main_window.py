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
from pg401_pyqt.controller.laser_api import list_command
from pg401_pyqt.controller.enums_commands import List


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PG401 - Control Láser")
        self.setGeometry(200, 200, 600, 400)

        # Layout principal
        main_layout = QVBoxLayout()

        # Sección de estado
        estado_group = QGroupBox("Estado del sistema")
        estado_layout = QHBoxLayout()
        self.label_estado = QLabel("Desconocido")
        self.label_estado.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        estado_layout.addWidget(QLabel("Estado del láser:"))
        estado_layout.addWidget(self.label_estado)
        estado_layout.addStretch()
        estado_group.setLayout(estado_layout)
        main_layout.addWidget(estado_group)

        # Sección de controles
        from PyQt6.QtWidgets import QGridLayout
        controles_group = QGroupBox("Comandos")
        controles_layout = QGridLayout()


        from PyQt6.QtWidgets import QLineEdit


        # LIST
        label_list = QLabel("LIST:")
        self.combo_list = QComboBox()
        self.combo_list.addItem("Seleccione un comando LIST...")
        self.combo_list.addItems(["SEQUENCES", "SEQUENCES/DISTINCT SEQUENCES", "CLOG", "CLOG WHERE TIME >", "MSG"])
        self.input_list_time = QLineEdit()
        self.input_list_time.setPlaceholderText("Ingrese tiempo")
        self.input_list_time.setVisible(False)
        controles_layout.addWidget(label_list, 0, 0)
        controles_layout.addWidget(self.combo_list, 0, 1)
        controles_layout.addWidget(self.input_list_time, 0, 2)
        self.btn_ejecutar_list = QPushButton("Ejecutar LIST")
        controles_layout.addWidget(self.btn_ejecutar_list, 0, 3)

        def on_list_changed(index):
            self.input_list_time.setVisible(self.combo_list.currentText() == "CLOG WHERE TIME >")
        self.combo_list.currentIndexChanged.connect(on_list_changed)

        def ejecutar_list():
            comando = self.combo_list.currentText()
            if comando == "Seleccione un comando LIST...":
                self.text_log.append("<span style='color:red;'>Seleccione un comando válido de LIST.</span>")
                return
            if comando == "CLOG WHERE TIME >":
                valor = self.input_list_time.text().strip()
                if not valor:
                    self.text_log.append("<span style='color:red;'>Ingrese un valor para el tiempo.</span>")
                    return
                respuesta = list_command(List.CLOG_WHERE, valor)
            elif comando == "SEQUENCES":
                respuesta = list_command(List.SEQUENCES)
            elif comando == "SEQUENCES/DISTINCT SEQUENCES":
                respuesta = list_command(List.SEQUENCES_DISTINCT)
            elif comando == "CLOG":
                respuesta = list_command(List.CLOG)
            elif comando == "MSG":
                respuesta = list_command(List.MSG)
            else:
                self.text_log.append("<span style='color:red;'>Comando no reconocido.</span>")
                return
            self.text_log.append(respuesta)

        self.btn_ejecutar_list.clicked.connect(ejecutar_list)

        # EXE
        label_exe = QLabel("EXE:")
        self.combo_exe = QComboBox()
        self.combo_exe.addItem("Seleccione un comando EXE...")
        self.combo_exe.addItems(["Stop", "Fire", "Amplification/"])
        self.input_exe_amp = QLineEdit()
        self.input_exe_amp.setPlaceholderText("Ingrese amplificación")
        self.input_exe_amp.setVisible(False)
        controles_layout.addWidget(label_exe, 1, 0)
        controles_layout.addWidget(self.combo_exe, 1, 1)
        controles_layout.addWidget(self.input_exe_amp, 1, 2)

        def on_exe_changed(index):
            self.input_exe_amp.setVisible(self.combo_exe.currentText() == "Amplification/")
        self.combo_exe.currentIndexChanged.connect(on_exe_changed)

        # RDVAR
        label_rdvar = QLabel("RDVAR:")
        self.combo_rdvar = QComboBox()
        self.combo_rdvar.addItem("Seleccione un comando RDVAR...")
        self.combo_rdvar.addItems(["State", "LogBlab", "ProductID", "ProductSN"])
        controles_layout.addWidget(label_rdvar, 2, 0)
        controles_layout.addWidget(self.combo_rdvar, 2, 1)

        # DATA
        label_data = QLabel("DATA:")
        self.combo_data = QComboBox()
        self.combo_data.addItem("Seleccione un comando DATA...")
        self.combo_data.addItems(["ChannelNo", "time"])
        self.input_data_channel = QLineEdit()
        self.input_data_channel.setPlaceholderText("Canal")
        self.input_data_channel.setVisible(False)
        self.input_data_time = QLineEdit()
        self.input_data_time.setPlaceholderText("Tiempo")
        self.input_data_time.setVisible(False)
        controles_layout.addWidget(label_data, 3, 0)
        controles_layout.addWidget(self.combo_data, 3, 1)
        controles_layout.addWidget(self.input_data_channel, 3, 2)
        controles_layout.addWidget(self.input_data_time, 3, 3)

        def on_data_changed(index):
            self.input_data_channel.setVisible(self.combo_data.currentText() == "ChannelNo")
            self.input_data_time.setVisible(self.combo_data.currentText() == "time")
        self.combo_data.currentIndexChanged.connect(on_data_changed)

        # CES
        label_ces = QLabel("CES:")
        self.combo_ces = QComboBox()
        self.combo_ces.addItem("Seleccione un comando CES...")
        self.combo_ces.addItems(["time"])
        self.input_ces_time = QLineEdit()
        self.input_ces_time.setPlaceholderText("Tiempo")
        self.input_ces_time.setVisible(False)
        controles_layout.addWidget(label_ces, 4, 0)
        controles_layout.addWidget(self.combo_ces, 4, 1)
        controles_layout.addWidget(self.input_ces_time, 4, 2)

        def on_ces_changed(index):
            self.input_ces_time.setVisible(self.combo_ces.currentText() == "time")
        self.combo_ces.currentIndexChanged.connect(on_ces_changed)

        controles_group.setLayout(controles_layout)
        main_layout.addWidget(controles_group)

        # Sección de logs/mensajes
        log_group = QGroupBox("Mensajes y logs")
        log_layout = QVBoxLayout()
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        log_layout.addWidget(self.text_log)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Espaciador para estética
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Contenedor central
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def consultar_estado(self):
        # Simulación: solo cambia el texto localmente y agrega un mensaje al log
        self.label_estado.setText("Idle (simulado)")
        self.text_log.append("[INFO] Estado consultado: Idle (simulado)")
