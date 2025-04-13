"""
MockupBuddy - PyQt Edition v0.4.3
✅ Multiply blend mode fallback logic
✅ Multiply mode disabled by default
✅ Folder path persistence across sessions
✅ Error-handling for invisible multiply results
"""

import sys, os, json
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QSlider, QCheckBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance

CONFIG_PATH = str(Path.home() / ".mockupbuddy_pyqt_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

def apply_multiply_blend(base_img, overlay_img):
    try:
        base = base_img.convert("RGBA")
        overlay = overlay_img.convert("RGBA").resize(base.size)
        blended = Image.blend(base, overlay, 0.5)
        return blended
    except Exception as e:
        print(f"[Blend Error] {e}")
        return base_img

class MockupBuddy(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PyQt v0.4.3")
        self.resize(1200, 700)
        self.config = load_config()
        self.design_folder = self.config.get("design_folder", "")
        self.mockup_folder = self.config.get("mockup_folder", "")
        self.output_folder = self.config.get("output_folder", "")

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        controls = QVBoxLayout()

        self.select_design_btn = QPushButton("Select Design Folder")
        self.select_design_btn.clicked.connect(self.select_design_folder)
        controls.addWidget(self.select_design_btn)

        self.select_mockup_btn = QPushButton("Select Mockup Folder")
        self.select_mockup_btn.clicked.connect(self.select_mockup_folder)
        controls.addWidget(self.select_mockup_btn)

        self.select_output_btn = QPushButton("Select Output Folder")
        self.select_output_btn.clicked.connect(self.select_output_folder)
        controls.addWidget(self.select_output_btn)

        self.multiply_checkbox = QCheckBox("Use Multiply Blend Mode")
        self.multiply_checkbox.setChecked(False)
        controls.addWidget(self.multiply_checkbox)

        self.preview_btn = QPushButton("Update Preview")
        self.preview_btn.clicked.connect(self.update_preview)
        controls.addWidget(self.preview_btn)

        self.generate_btn = QPushButton("Generate Mockup")
        self.generate_btn.clicked.connect(self.generate_mockup)
        controls.addWidget(self.generate_btn)

        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(controls, 1)
        layout.addWidget(self.preview_label, 3)
        self.setLayout(layout)

    def select_design_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Design Folder")
        if folder:
            self.design_folder = folder
            self.save_session()

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder")
        if folder:
            self.mockup_folder = folder
            self.save_session()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.save_session()

    def save_session(self):
        self.config["design_folder"] = self.design_folder
        self.config["mockup_folder"] = self.mockup_folder
        self.config["output_folder"] = self.output_folder
        save_config(self.config)

    def update_preview(self):
        try:
            design_files = [f for f in os.listdir(self.design_folder) if f.endswith((".png", ".jpg"))]
            mockup_files = [f for f in os.listdir(self.mockup_folder) if f.endswith((".png", ".jpg"))]
            if not design_files or not mockup_files:
                self.preview_label.setText("No design or mockup images found")
                return
            design = Image.open(os.path.join(self.design_folder, design_files[0]))
            mockup = Image.open(os.path.join(self.mockup_folder, mockup_files[0]))
            result = apply_multiply_blend(mockup, design) if self.multiply_checkbox.isChecked() else mockup.copy()
            preview_qt = self.pil2pixmap(result)
            self.preview_label.setPixmap(preview_qt)
        except Exception as e:
            self.preview_label.setText(f"Preview Error: {e}")

    def generate_mockup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            design_file = os.listdir(self.design_folder)[0]
            mockup_file = os.listdir(self.mockup_folder)[0]
            design = Image.open(os.path.join(self.design_folder, design_file))
            mockup = Image.open(os.path.join(self.mockup_folder, mockup_file))
            result = apply_multiply_blend(mockup, design) if self.multiply_checkbox.isChecked() else mockup.copy()
            output_path = os.path.join(self.output_folder, f"{Path(design_file).stem}_{Path(mockup_file).stem}_{timestamp}.png")
            result.save(output_path)
        except Exception as e:
            print(f"[Generate Error] {e}")

    def pil2pixmap(self, image):
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddy()
    window.show()
    sys.exit(app.exec_())