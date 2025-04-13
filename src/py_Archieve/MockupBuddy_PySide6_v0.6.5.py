# MockupBuddy_PySide6_v0.6.5
# - Slider layout containment (design size, opacity, offsets)
# - UI margin and spacing refinements
# - All features from v0.6.4a preserved

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QSlider, QFileDialog, QScrollArea, QListWidget, QListWidgetItem, QProgressBar,
    QTextEdit, QCheckBox, QComboBox, QSizePolicy, QFrame
)
from PySide6.QtGui import QPixmap, QImage, QAction, QIcon
from PySide6.QtCore import Qt, QTimer, QSize
from PIL import Image, ImageQt
import os

class MockupBuddyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PySide6 v0.6.5")
        self.resize(1280, 900)

        # Paths
        self.design_folder = ""
        self.mockup_folder = ""
        self.output_folder = ""

        # Layout
        self.main_layout = QHBoxLayout(self)
        self.sidebar = QVBoxLayout()
        self.control_frame = QWidget()
        self.control_frame.setLayout(self.sidebar)
        self.control_frame.setFixedWidth(360)
        self.control_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.preview_area = QLabel("Mockup Preview", alignment=Qt.AlignCenter)
        self.preview_area.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.preview_area.setMinimumSize(800, 600)

        self.main_layout.addWidget(self.control_frame)
        self.main_layout.addWidget(self.preview_area)

        # Controls
        self.build_controls()

        # Status Log
        self.log_box = QTextEdit()
        self.log_box.setFixedHeight(100)
        self.log_box.setReadOnly(True)
        self.main_layout.addWidget(self.log_box)

    def build_controls(self):
        # Folder selectors
        btn_style = "text-align: left; padding: 6px; font-weight: bold;"

        self.btn_design = QPushButton("📂 Select Design Folder")
        self.btn_design.setStyleSheet(btn_style)
        self.btn_design.clicked.connect(lambda: self.select_folder("design"))

        self.btn_mockup = QPushButton("🎨 Select Mockup Folder")
        self.btn_mockup.setStyleSheet(btn_style)
        self.btn_mockup.clicked.connect(lambda: self.select_folder("mockup"))

        self.btn_output = QPushButton("💾 Select Output Folder")
        self.btn_output.setStyleSheet(btn_style)
        self.btn_output.clicked.connect(lambda: self.select_folder("output"))

        self.btn_generate = QPushButton("🚀 Generate Mockups")
        self.btn_generate.setStyleSheet(btn_style)

        self.sidebar.addWidget(self.btn_design)
        self.sidebar.addWidget(self.btn_mockup)
        self.sidebar.addWidget(self.btn_output)
        self.sidebar.addWidget(self.btn_generate)

        self.add_divider()

        # Sliders
        self.slider_opacity = self.create_slider("Opacity", 0, 100, 100)
        self.slider_size = self.create_slider("Size", 100, 1000, 400)
        self.slider_x = self.create_slider("X Offset", -500, 500, 0)
        self.slider_y = self.create_slider("Y Offset", -500, 500, 0)

        self.add_divider()

        # Coffee button (icon-based)
        self.coffee_button = QPushButton()
        coffee_icon = QIcon(os.path.join(os.path.dirname(__file__), "..", "assets", "bmcNT.png"))
        self.coffee_button.setIcon(coffee_icon)
        self.coffee_button.setIconSize(QSize(140, 39))
        self.coffee_button.setFixedSize(150, 45)
        self.sidebar.addWidget(self.coffee_button)

        self.sidebar.addStretch()

    def create_slider(self, label, min_val, max_val, default_val):
        lbl = QLabel(label)
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickInterval((max_val - min_val) // 10)
        slider.setSingleStep(1)

        wrapper = QVBoxLayout()
        wrapper.addWidget(lbl)
        wrapper.addWidget(slider)

        frame = QFrame()
        frame.setLayout(wrapper)
        frame.setStyleSheet("padding: 4px;")
        self.sidebar.addWidget(frame)

        return slider

    def add_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("margin: 10px 0;")
        self.sidebar.addWidget(line)

    def select_folder(self, folder_type):
        folder = QFileDialog.getExistingDirectory(self, f"Select {folder_type.capitalize()} Folder")
        if folder:
            setattr(self, f"{folder_type}_folder", folder)
            self.log(f"{folder_type.capitalize()} folder set to: {folder}")

    def log(self, message):
        self.log_box.append(message)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MockupBuddyApp()
    window.show()
    sys.exit(app.exec())
