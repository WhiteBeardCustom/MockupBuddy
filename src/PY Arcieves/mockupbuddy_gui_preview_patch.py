
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QSpinBox, QCheckBox, QGroupBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image

class MockupBuddyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PyQt Edition")
        self.resize(1200, 800)
        self.design_path = None
        self.mockup_path = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Sidebar
        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar, 1)

        self.preview_label = QLabel("Preview will show here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #222; color: white;")
        main_layout.addWidget(self.preview_label, 2)

        # Folder selectors
        self.design_label = QLabel("Design: Not Selected")
        sidebar.addWidget(self.design_label)
        sidebar.addWidget(QPushButton("Select Design Image", clicked=self.select_design_file))

        self.mockup_label = QLabel("Mockup: Not Selected")
        sidebar.addWidget(self.mockup_label)
        sidebar.addWidget(QPushButton("Select Mockup Image", clicked=self.select_mockup_file))

        # Size & Opacity sliders
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(10)
        self.size_slider.setMaximum(200)
        self.size_slider.setValue(100)
        self.size_slider.valueChanged.connect(self.update_preview)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_preview)

        sidebar.addWidget(QLabel("Size %"))
        sidebar.addWidget(self.size_slider)
        sidebar.addWidget(QLabel("Opacity %"))
        sidebar.addWidget(self.opacity_slider)

        sidebar.addWidget(QPushButton("Update Preview", clicked=self.update_preview))

    def select_design_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Design Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.design_path = path
            self.design_label.setText(f"Design: {os.path.basename(path)}")
            self.update_preview()

    def select_mockup_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Mockup Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.mockup_path = path
            self.mockup_label.setText(f"Mockup: {os.path.basename(path)}")
            self.update_preview()

    def update_preview(self):
        if not self.design_path or not self.mockup_path:
            return

        try:
            mockup_img = Image.open(self.mockup_path).convert("RGBA")
            design_img = Image.open(self.design_path).convert("RGBA")

            # Scale design image
            scale = self.size_slider.value() / 100.0
            new_size = (int(design_img.width * scale), int(design_img.height * scale))
            design_img = design_img.resize(new_size, Image.LANCZOS)

            # Apply opacity
            alpha = design_img.split()[3]
            alpha = alpha.point(lambda p: int(p * (self.opacity_slider.value() / 100)))
            design_img.putalpha(alpha)

            # Center design on mockup
            x = (mockup_img.width - design_img.width) // 2
            y = (mockup_img.height - design_img.height) // 2
            mockup_img.paste(design_img, (x, y), design_img)

            # Convert to QPixmap for preview
            qimage = QImage(mockup_img.tobytes("raw", "RGBA"), mockup_img.width, mockup_img.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        except Exception as e:
            self.preview_label.setText(f"[Preview Error]\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddyApp()
    window.show()
    sys.exit(app.exec_())
