# taslak.py — Kimyasal Saldırı Simülasyonu & Harita (PyQt5 + QtWebEngine)

import csv
import sys
import time
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QComboBox, QSizePolicy
)
# --- Additional imports for embedded map ---
import folium
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
import matplotlib.pyplot as plt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kimyasal Saldırı Simülasyonu")
        self.resize(1000, 700)

        # 1) Simüle edilebilecek kimyasal ajan tipleri ve parametreleri
        self.attack_types = {
            'Sarin':      {'mean': 70.0, 'std': 10.0},
            'Chlorine':   {'mean': 50.0, 'std': 15.0},
            'MustardGas': {'mean': 30.0, 'std': 20.0},
        }

        # Base coordinates for marker movement
        self.base_lat = 39.0
        self.base_lon = 35.0

        # Merkezi widget + layout
        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        # 2) Kimyasal ajan seçimi
        self.combo = QComboBox()
        self.combo.addItems(self.attack_types.keys())
        layout.addWidget(self.combo)

        # Coordinate inputs (hidden until map shown)
        self.coord_widget = QWidget()
        coord_layout = QHBoxLayout(self.coord_widget)
        coord_layout.addWidget(QLabel("Latitude:"))
        self.lat_input = QLineEdit(str(self.base_lat))
        coord_layout.addWidget(self.lat_input)
        coord_layout.addWidget(QLabel("Longitude:"))
        self.lon_input = QLineEdit(str(self.base_lon))
        coord_layout.addWidget(self.lon_input)
        layout.addWidget(self.coord_widget)
        self.coord_widget.setVisible(False)

        # Manual value input (hidden until map shown)
        self.val_widget = QWidget()
        val_layout = QHBoxLayout(self.val_widget)
        val_layout.addWidget(QLabel("Değer (0–100):"))
        self.value_input = QLineEdit("0.0")
        val_layout.addWidget(self.value_input)
        layout.addWidget(self.val_widget)
        self.val_widget.setVisible(False)

        # 3) Simülasyon sonucu gösterecek etiket
        self.status_label = QLabel("", self)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.status_label)

        # 4) Sesli uyarı aç/kapa butonu
        self.beep_enabled = True
        self.mute_btn = QPushButton("Sesli Uyarı: Açık", self)
        self.mute_btn.clicked.connect(self.toggle_beep)
        layout.addWidget(self.mute_btn)

        # Grafik açma butonu
        self.graph_btn = QPushButton("Grafik Aç", self)
        self.graph_btn.clicked.connect(self.open_graph)
        layout.addWidget(self.graph_btn)

        # Embedded map below other widgets
        self.webview = QWebEngineView()
        self.webview.hide()
        # Use a default Leaflet map
        layout.addWidget(self.webview, stretch=1)

        # Haritayı göster butonu
        self.map_btn = QPushButton("Haritayı Göster", self)
        self.map_btn.clicked.connect(self.show_map)
        layout.addWidget(self.map_btn)


    def update_ui(self):
        bije = self.combo.currentText()
        params = self.attack_types[bije]
        # read manual value
        try:
            val = float(self.value_input.text())
        except ValueError:
            val = 0.0
        val = max(0.0, min(100.0, val))
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        self.status_label.setText(f"{ts}\n{bije} konsantrasyonu: {val:.2f}")
        # audio alert if above mean and update last_event_time
        if val > params['mean'] and self.beep_enabled:
            QApplication.beep()
            self.last_event_time = time.time()

    def toggle_beep(self):
        # Toggle beep on/off
        self.beep_enabled = not self.beep_enabled
        state = "Açık" if self.beep_enabled else "Kapalı"
        self.mute_btn.setText(f"Sesli Uyarı: {state}")

    def log_data(self, agent, value):
        log_file = "data_log.csv"
        header = not os.path.exists(log_file)
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(["timestamp", "agent", "value"])
            writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), agent, f"{value:.2f}"])


    def reload_map(self):
        # Generate a simple Folium map and load it
        try:
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
        except ValueError:
            lat, lon = self.base_lat, self.base_lon
        m = folium.Map(location=[lat, lon], zoom_start=7)
        folium.Marker([lat, lon], popup="Center Location").add_to(m)
        m.save("map.html")
        self.webview.load(QUrl.fromLocalFile(os.path.abspath("map.html")))

    def open_graph(self):
        # Örnek grafik: manuel değerin zaman içinde değişimini gösterir
        # Burada basit bir zaman ekseni ve sabit değer gösteriyoruz
        values = []
        times = list(range(10))
        try:
            val = float(self.value_input.text())
        except ValueError:
            val = 0.0
        # Aynı değeri 10 nokta için tekrar kullan
        values = [val for _ in times]

        plt.figure("Simülasyon Grafiği")
        plt.plot(times, values, marker='o')
        plt.xlabel("Zaman (saniye)")
        plt.ylabel("Değer")
        plt.title("Manuel Girilen Konsantrasyon")
        plt.grid(True)
        plt.show()

    def show_map(self):
        # Toggle map visibility and button text
        if not self.webview.isVisible():
            # Show map
            self.resize(1000, 700)
            self.webview.show()
            self.reload_map()
            self.map_btn.setText("Haritayı Gizle")
            self.coord_widget.setVisible(True)
            self.val_widget.setVisible(True)
        else:
            # Hide map
            self.webview.hide()
            self.map_btn.setText("Haritayı Göster")
            self.coord_widget.setVisible(False)
            self.val_widget.setVisible(False)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()