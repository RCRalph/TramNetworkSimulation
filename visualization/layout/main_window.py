from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from visualization.layout.folium_map_widget import FoliumMapWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tram Network Simulation")
        self.showMaximized()

        layout = QVBoxLayout()
        layout.addWidget(FoliumMapWidget())

        window_widget = QWidget()
        window_widget.setLayout(layout)

        self.setCentralWidget(window_widget)
