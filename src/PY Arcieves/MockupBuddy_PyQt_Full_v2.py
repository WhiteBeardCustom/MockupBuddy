"""
MockupBuddy - Full PyQt5 Version v2
Includes: Folder selection, image preview, basic overlay handling.
"""

import sys
import os
import json
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QLineEdit, QCheckBox, QGroupBox,
    QMessageBox, QScrollArea, QGridLayout, QSizePolicy, QGraphicsView,
    QGraphicsScene, QSpacerItem, QTabWidget, QPlainTextEdit, QListWidget
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt

from PIL import Image, ImageQt

CONFIG_PATH = os.path.expanduser("~/.wbmockup_config.json")

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
        self.resize(1400, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.design_images = []
        self.mockup_images = []

        self.init_ui()
        self.load_config()

    def init_ui(self):
        # Left panel
        self.left_panel = QVBoxLayout()
        self.main_layout.addLayout(self.left_panel, 1)

        self.design_folder_button = QPushButton("Select Design Folder")
        self.design_folder_button.clicked.connect(self.select_design_folder)
        self.left_panel.addWidget(self.design_folder_button)

        self.mockup_folder_button = QPushButton("Select Mockup Folder")
        self.mockup_folder_button.clicked.connect(self.select_mockup_folder)
        self.left_panel.addWidget(self.mockup_folder_button)

        self.output_folder_button = QPushButton("Select Output Folder")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        self.left_panel.addWidget(self.output_folder_button)

        self.design_list = QListWidget()
        self.design_list.itemClicked.connect(self.load_preview)
        self.left_panel.addWidget(QLabel("Design Files:"))
        self.left_panel.addWidget(self.design_list, 5)

        self.mockup_list = QListWidget()
        self.mockup_list.itemClicked.connect(self.load_preview)
        self.left_panel.addWidget(QLabel("Mockup Files:"))
        self.left_panel.addWidget(self.mockup_list, 5)

        # Right panel
        self.right_panel = QVBoxLayout()
        self.main_layout.addLayout(self.right_panel, 3)

        self.preview_label = QLabel("Preview:")
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

        if self.design_folder:
            self.populate_design_list()
        if self.mockup_folder:
            self.populate_mockup_list()

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
            self.populate_design_list()

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder", self.mockup_folder or os.getcwd())
        if folder:
            self.mockup_folder = folder
            self.save_config()
            self.populate_mockup_list()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder or os.getcwd())
        if folder:
            self.output_folder = folder
            self.save_config()

    def populate_design_list(self):
        self.design_list.clear()
        if os.path.isdir(self.design_folder):
            for fname in os.listdir(self.design_folder):
                if fname.lower().endswith(".png"):
                    self.design_list.addItem(fname)

    def populate_mockup_list(self):
        self.mockup_list.clear()
        if os.path.isdir(self.mockup_folder):
            for fname in os.listdir(self.mockup_folder):
                if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    self.mockup_list.addItem(fname)

    def load_preview(self):
        design_item = self.design_list.currentItem()
        mockup_item = self.mockup_list.currentItem()
        if not design_item or not mockup_item:
            return

        design_path = os.path.join(self.design_folder, design_item.text())
        mockup_path = os.path.join(self.mockup_folder, mockup_item.text())

        try:
            mockup_img = Image.open(mockup_path).convert("RGBA")
            design_img = Image.open(design_path).convert("RGBA")

            # Resize design to fit mockup (simple centered logic for now)
            mw, mh = mockup_img.size
            scale = 0.3
            new_w = int(mw * scale)
            design_scaled = design_img.resize((new_w, int(new_w * design_img.height / design_img.width)))

            dx = (mw - design_scaled.width) // 2
            dy = (mh - design_scaled.height) // 2
            mockup_img.paste(design_scaled, (dx, dy), design_scaled)

            preview_qt = ImageQt.ImageQt(mockup_img)
            pixmap = QPixmap.fromImage(preview_qt)
            self.graphics_scene.clear()
            self.graphics_scene.addPixmap(pixmap)
            self.graphics_view.fitInView(self.graphics_scene.sceneRect(), Qt.KeepAspectRatio)
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Could not generate preview:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddyApp()
    window.show()
    sys.exit(app.exec_())
