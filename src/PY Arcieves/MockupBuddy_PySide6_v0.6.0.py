import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSlider, QScrollArea, QTextEdit, QFrame, QSizePolicy
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
        self.setWindowTitle("MockupBuddy - PySide6 v0.6.2")
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
        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(control_container)

        # Controls
        self.design_button = QPushButton("📂 Select Design Folder")
        self.mockup_button = QPushButton("🎨 Select Mockup Folder")
        self.output_button = QPushButton("💾 Select Output Folder")
        self.generate_button = QPushButton("🚀 Generate Mockups")

        self.design_button.clicked.connect(self.select_design_folder)
        self.mockup_button.clicked.connect(self.select_mockup_folder)
        self.output_button.clicked.connect(self.select_output_folder)
        self.generate_button.clicked.connect(self.generate_mockups)

        for btn in [self.design_button, self.mockup_button, self.output_button, self.generate_button]:
            btn.setMinimumHeight(35)
            control_layout.addWidget(btn)

        # Slider with label
        opacity_label = QLabel("Opacity")
        opacity_label.setAlignment(Qt.AlignLeft)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_preview)

        slider_row = QVBoxLayout()
        slider_row.addWidget(opacity_label)
        slider_row.addWidget(self.opacity_slider)
        control_layout.addLayout(slider_row)

        # Coffee Button
        coffee_path = get_asset_path("bmcNT.png")
        if os.path.exists(coffee_path):
            pixmap = QPixmap(coffee_path)
            coffee_button = QPushButton()
            coffee_button.setIcon(QIcon(pixmap))
            coffee_button.setIconSize(pixmap.size())
            coffee_button.setFixedSize(pixmap.size())
            coffee_button.setCursor(Qt.PointingHandCursor)
            coffee_button.setStyleSheet("border: none;")
            coffee_button.clicked.connect(lambda: os.system("open https://www.buymeacoffee.com/nicktrautman"))
            control_layout.addWidget(coffee_button)

        control_layout.addStretch()

        # RIGHT: Preview + Debug Area
        right_panel = QVBoxLayout()

        self.preview_label = QLabel("Mockup Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #222; color: white;")
        self.preview_label.setMinimumHeight(600)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel.addWidget(self.preview_label, 5)

        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setMaximumHeight(100)
        self.debug_output.setStyleSheet("background-color: #f0f0f0; color: #333;")
        right_panel.addWidget(self.debug_output, 1)

        layout.addWidget(scroll, 2)
        layout.addLayout(right_panel, 5)

        self.update_preview()

    def log(self, message):
        self.debug_output.append(message)

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
            design_img.putalpha(int(255 * (self.opacity_slider.value() / 100.0)))
            mockup_img.paste(design_img, (50, 50), design_img)
            qt_img = QPixmap.fromImage(ImageQt.ImageQt(mockup_img))
            self.preview_label.setPixmap(qt_img.scaled(
                self.preview_label.width(), self.preview_label.height(), Qt.KeepAspectRatio))
            self.log(f"Preview updated with: {designs[0]} + {mockups[0]}")
        except Exception as e:
            self.log(f"Preview error: {e}")
            self.preview_label.setText("Preview Error")

    def generate_mockups(self):
        self.log("[TODO] Generate mockup functionality not yet implemented.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockupBuddy()
    window.show()
    sys.exit(app.exec())