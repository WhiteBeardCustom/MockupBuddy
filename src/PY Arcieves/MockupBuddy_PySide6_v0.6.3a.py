import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSlider, QScrollArea, QTextEdit, QSizePolicy,
    QComboBox, QCheckBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PIL import Image, ImageQt

CONFIG_PATH = os.path.expanduser("~/.wbmockup_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            return json.load(open(CONFIG_PATH))
        except:
            pass
    return {}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

def get_asset_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'Resources'))
    else:
        base_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
    return os.path.join(base_path, filename)

def apply_opacity(image, opacity):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    alpha = image.getchannel('A').point(lambda p: int(p * opacity))
    image.putalpha(alpha)
    return image

class MockupBuddy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PySide6 v0.6.3a")
        self.resize(1200, 800)

        self.config = load_config()
        self.design_folder = self.config.get("design_folder", "")
        self.mockup_folder = self.config.get("mockup_folder", "")
        self.output_folder = self.config.get("output_folder", "")

        self.selected_design = None
        self.selected_mockup = None

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(12)

        control_scroll.setWidget(control_container)

        # Folder Buttons + Labels
        self.design_button = QPushButton("📂 Select Design Folder")
        self.design_button.clicked.connect(self.select_design_folder)
        self.design_label = QLabel("(No folder selected)")

        self.mockup_button = QPushButton("🎨 Select Mockup Folder")
        self.mockup_button.clicked.connect(self.select_mockup_folder)
        self.mockup_label = QLabel("(No folder selected)")

        self.output_button = QPushButton("💾 Select Output Folder")
        self.output_button.clicked.connect(self.select_output_folder)
        self.output_label = QLabel("(No folder selected)")

        control_layout.addWidget(self.design_button)
        control_layout.addWidget(self.design_label)
        control_layout.addWidget(self.mockup_button)
        control_layout.addWidget(self.mockup_label)
        control_layout.addWidget(self.output_button)
        control_layout.addWidget(self.output_label)

        # Dropdowns
        self.design_dropdown = QComboBox()
        self.mockup_dropdown = QComboBox()
        self.design_dropdown.currentIndexChanged.connect(self.update_preview)
        self.mockup_dropdown.currentIndexChanged.connect(self.update_preview)
        control_layout.addWidget(QLabel("Select Design"))
        control_layout.addWidget(self.design_dropdown)
        control_layout.addWidget(QLabel("Select Mockup"))
        control_layout.addWidget(self.mockup_dropdown)

        # Sliders and Lock Toggle
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(50, 1000)
        self.size_slider.setValue(400)
        self.size_slider.valueChanged.connect(self.update_preview)
        control_layout.addWidget(QLabel("Design Size"))
        control_layout.addWidget(self.size_slider)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_preview)
        control_layout.addWidget(QLabel("Opacity"))
        control_layout.addWidget(self.opacity_slider)

        self.x_offset_slider = QSlider(Qt.Horizontal)
        self.x_offset_slider.setRange(-500, 500)
        self.x_offset_slider.setValue(0)
        self.x_offset_slider.valueChanged.connect(self.update_preview)
        control_layout.addWidget(QLabel("X Offset"))
        control_layout.addWidget(self.x_offset_slider)

        self.y_offset_slider = QSlider(Qt.Horizontal)
        self.y_offset_slider.setRange(-500, 500)
        self.y_offset_slider.setValue(0)
        self.y_offset_slider.valueChanged.connect(self.update_preview)
        control_layout.addWidget(QLabel("Y Offset"))
        control_layout.addWidget(self.y_offset_slider)

        self.lock_aspect_checkbox = QCheckBox("Lock Aspect Ratio")
        self.lock_aspect_checkbox.setChecked(True)
        self.lock_aspect_checkbox.stateChanged.connect(self.update_preview)
        control_layout.addWidget(self.lock_aspect_checkbox)

        self.generate_button = QPushButton("🚀 Generate Mockups")
        self.generate_button.clicked.connect(self.generate_mockups)
        control_layout.addWidget(self.generate_button)

        # Coffee Button
        coffee_path = get_asset_path("bmcNT.png")
        if os.path.exists(coffee_path):
            coffee_pixmap = QPixmap(coffee_path).scaled(140, 39, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            coffee_btn = QPushButton()
            coffee_btn.setIcon(QIcon(coffee_pixmap))
            coffee_btn.setIconSize(coffee_pixmap.size())
            coffee_btn.setFixedSize(coffee_pixmap.size())
            coffee_btn.setCursor(Qt.PointingHandCursor)
            coffee_btn.setStyleSheet("border: none;")
            coffee_btn.clicked.connect(lambda: os.system("open https://www.buymeacoffee.com/nicktrautman"))
            control_layout.addWidget(coffee_btn)

        control_layout.addStretch()

        # Right Panel
        right_layout = QVBoxLayout()
        self.preview_label = QLabel("Mockup Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #222; color: white;")
        self.preview_label.setMinimumHeight(600)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.preview_label, 5)

        self.debug_log = QTextEdit()
        self.debug_log.setReadOnly(True)
        self.debug_log.setMaximumHeight(120)
        right_layout.addWidget(self.debug_log)

        layout.addWidget(control_scroll, 2)
        layout.addLayout(right_layout, 5)

        self.update_preview()

    def log(self, message):
        self.debug_log.append(message)

    def select_design_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Design Folder", self.design_folder)
        if folder:
            self.design_folder = folder
            self.config['design_folder'] = folder
            save_config(self.config)
            self.design_label.setText(folder)
            self.populate_dropdown(self.design_dropdown, self.design_folder)

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder", self.mockup_folder)
        if folder:
            self.mockup_folder = folder
            self.config['mockup_folder'] = folder
            save_config(self.config)
            self.mockup_label.setText(folder)
            self.populate_dropdown(self.mockup_dropdown, self.mockup_folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.config['output_folder'] = folder
            save_config(self.config)
            self.output_label.setText(folder)

    def populate_dropdown(self, dropdown, folder):
        dropdown.clear()
        if not os.path.isdir(folder):
            return
        files = [f for f in os.listdir(folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        dropdown.addItems(files)

    def update_preview(self):
        if not (self.mockup_folder and self.design_folder):
            return

        design_name = self.design_dropdown.currentText()
        mockup_name = self.mockup_dropdown.currentText()

        if not (design_name and mockup_name):
            return

        design_path = os.path.join(self.design_folder, design_name)
        mockup_path = os.path.join(self.mockup_folder, mockup_name)

        try:
            mockup_img = Image.open(mockup_path).convert("RGBA")
            design_img = Image.open(design_path).convert("RGBA")

            w, h = design_img.size
            if self.lock_aspect_checkbox.isChecked():
                scale = self.size_slider.value() / max(w, h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w = new_h = self.size_slider.value()

            design_img = design_img.resize((new_w, new_h), Image.LANCZOS)
            design_img = apply_opacity(design_img, self.opacity_slider.value() / 100.0)

            x = (mockup_img.width - new_w) // 2 + self.x_offset_slider.value()
            y = (mockup_img.height - new_h) // 2 + self.y_offset_slider.value()
            mockup_img.paste(design_img, (x, y), design_img)

            qt_img = QPixmap.fromImage(ImageQt.ImageQt(mockup_img))
            self.preview_label.setPixmap(qt_img.scaled(
                self.preview_label.width(), self.preview_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.log(f"Preview: {design_name} + {mockup_name}")

        except Exception as e:
            self.log(f"Preview error: {e}")

    def generate_mockups(self):
        self.log("[TODO] Batch generation not implemented yet.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockupBuddy()
    window.show()
    sys.exit(app.exec())