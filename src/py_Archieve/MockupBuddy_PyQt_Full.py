"""
MockupBuddy - Full PyQt5 Version
Converted from: MockupBuddy_Full_EnhancedUX_RESTORED_PATCHED.py
"""

import sys
import os
import json
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QLineEdit, QCheckBox, QGroupBox,
    QMessageBox, QScrollArea, QGridLayout, QSizePolicy, QGraphicsView,
    QGraphicsScene, QSpacerItem, QTabWidget, QPlainTextEdit
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QTimer

from PIL import Image, ImageQt

CONFIG_PATH = os.path.expanduser("~/.wbmockup_config.json")
TEMPLATES_PATH = os.path.expanduser("~/.wbmockup_templates.json")
DESIGN_SETTINGS_PATH = os.path.expanduser("~/.wbmockup_design_settings.json")

class Mockup:
    def __init__(self, path, is_dark=False):
        self.path = path
        self.filename = os.path.basename(path)
        self.is_dark = is_dark

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[JSON Load Error] {path} - {e}")
    return {}

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[JSON Save Error] {path} - {e}")

def is_light_design(filename):
    filename = os.path.basename(filename).lower().strip()
    return re.search(r'[\-_ ]light(\.|\s|$)', filename)

def is_dark_design(filename):
    filename = os.path.basename(filename).lower().strip()
    return re.search(r'[\-_ ]dark(\.|\s|$)', filename)

def get_design_basename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    base = re.sub(r'(?i)[\s\-_]*\b(light|dark)\b\s*$', '', base)
    base = re.sub(r'[-_\s]+$', '', base)  # Clean trailing junk
    return re.sub(r'[\s\-]+', '_', base.strip())  # Normalize

class MockupBuddyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy Pro - PyQt Version")
        self.resize(1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.init_ui()
        self.load_config()

    def init_ui(self):
        # Placeholder: Left Panel (Controls)
        self.left_panel = QVBoxLayout()
        self.main_layout.addLayout(self.left_panel, 1)

        # Placeholder: Right Panel (Preview)
        self.right_panel = QVBoxLayout()
        self.main_layout.addLayout(self.right_panel, 3)

        # Folder Selectors
        self.design_folder_button = QPushButton("Select Design Folder")
        self.design_folder_button.clicked.connect(self.select_design_folder)
        self.left_panel.addWidget(self.design_folder_button)

        self.mockup_folder_button = QPushButton("Select Mockup Folder")
        self.mockup_folder_button.clicked.connect(self.select_mockup_folder)
        self.left_panel.addWidget(self.mockup_folder_button)

        self.output_folder_button = QPushButton("Select Output Folder")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        self.left_panel.addWidget(self.output_folder_button)

        # Preview Canvas
        self.preview_label = QLabel("Mockup Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.right_panel.addWidget(self.preview_label)

        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.right_panel.addWidget(self.graphics_view)

    def load_config(self):
        self.config = load_json(CONFIG_PATH)
        self.design_folder = self.config.get("design_folder", "")
        self.mockup_folder = self.config.get("mockup_folder", "")
        self.output_folder = self.config.get("output_folder", "")

    def save_config(self):
        self.config["design_folder"] = self.design_folder
        self.config["mockup_folder"] = self.mockup_folder
        self.config["output_folder"] = self.output_folder
        save_json(CONFIG_PATH, self.config)

    def select_design_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Design Folder", self.design_folder or os.getcwd())
        if folder:
            self.design_folder = folder
            self.save_config()

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder", self.mockup_folder or os.getcwd())
        if folder:
            self.mockup_folder = folder
            self.save_config()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder or os.getcwd())
        if folder:
            self.output_folder = folder
            self.save_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddyApp()
    window.show()
    sys.exit(app.exec_())
