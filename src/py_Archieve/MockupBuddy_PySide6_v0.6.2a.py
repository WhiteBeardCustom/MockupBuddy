import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSlider, QScrollArea, QTextEdit, QSizePolicy
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

class MockupBuddy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PySide6 v0.6.2a")
        self.resize(1200, 800)

        self.config = load_config()
        self.design_folder = self.config.get("design_folder", "")
        self.mockup_folder = self.config.get("mockup_folder", "")
        self.output_folder = self.config.get("output_folder", "")

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # LEFT: Scrollable Control Panel
        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(12)

        control_scroll.setWidget(control_container)

        # Controls
        self.design_button = QPushButton("📂 Select Design Folder")
        self.mockup_button = QPushButton("🎨 Select Mockup Folder")
        self.output_button = QPushButton("💾 Select Output Folder")
        self.generate_button = QPushButton("🚀 Generate Mockups")

        for btn in [self.design_button, self.mockup_button, self.output_button, self.generate_button]:
            btn.setMinimumHeight(35)
            control_layout.addWidget(btn)

        self.design_button.clicked.connect(self.select_design_folder)
        self.mockup_button.clicked.connect(self.select_mockup_folder)
        self.output_button.clicked.connect(self.select_output_folder)
        self.generate_button.clicked.connect(self.generate_mockups)

        # Opacity Slider
        opacity_label = QLabel("Opacity")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_preview)

        control_layout.addWidget(opacity_label)
        control_layout.addWidget(self.opacity_slider)

        # Coffee button with size constraints
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

        # RIGHT: Preview and Log Area
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
            self.update_preview()

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder", self.mockup_folder)
        if folder:
            self.mockup_folder = folder
            self.config['mockup_folder'] = folder
            save_config(self.config)
            self.update_preview()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.config['output_folder'] = folder
            save_config(self.config)

    def update_preview(self):
        if not (self.mockup_folder and self.design_folder):
            self.log("Please select design and mockup folders.")
            return

        mockups = [f for f in os.listdir(self.mockup_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        designs = [f for f in os.listdir(self.design_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        if not (mockups and designs):
            self.log("No mockup or design files found.")
            return

        mockup_path = os.path.join(self.mockup_folder, mockups[0])
        design_path = os.path.join(self.design_folder, designs[0])

        try:
            mockup_img = Image.open(mockup_path).convert("RGBA")
            design_img = Image.open(design_path).convert("RGBA")
            opacity = self.opacity_slider.value() / 100.0
            alpha = design_img.split()[3].point(lambda p: int(p * opacity))
            design_img.putalpha(alpha)

            # Resize design relative to mockup for overlay
            design_img.thumbnail((mockup_img.width // 2, mockup_img.height // 2))
            x = (mockup_img.width - design_img.width) // 2
            y = (mockup_img.height - design_img.height) // 2

            mockup_img.paste(design_img, (x, y), design_img)
            qt_img = QPixmap.fromImage(ImageQt.ImageQt(mockup_img))
            self.preview_label.setPixmap(qt_img.scaled(
                self.preview_label.width(), self.preview_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.log(f"Preview updated with: {os.path.basename(design_path)} + {os.path.basename(mockup_path)}")
        except Exception as e:
            self.preview_label.setText("Preview Error")
            self.log(f"Error: {e}")

    def generate_mockups(self):
        self.log("[TODO] Batch generation not implemented yet.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockupBuddy()
    window.show()
    sys.exit(app.exec())