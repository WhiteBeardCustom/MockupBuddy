# MockupBuddy - PyQt Edition v0.3
# ✅ Adds Design Folder & Mockup Folder selection
# ✅ Loads all image files in selected folders
# ✅ Buttons to cycle through mockup/design previews
# ✅ Preview updates on selection change

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QCheckBox, QGroupBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image

SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.webp')

class MockupBuddyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PyQt v0.3")
        self.resize(1200, 800)

        self.design_folder = None
        self.mockup_folder = None
        self.design_files = []
        self.mockup_files = []
        self.current_design_index = 0
        self.current_mockup_index = 0

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

        # Folder Selectors
        sidebar.addWidget(QPushButton("Select Design Folder", clicked=self.select_design_folder))
        self.design_nav_label = QLabel("Design: Not Selected")
        sidebar.addWidget(self.design_nav_label)
        sidebar.addWidget(QPushButton("Prev Design", clicked=self.prev_design))
        sidebar.addWidget(QPushButton("Next Design", clicked=self.next_design))

        sidebar.addWidget(QPushButton("Select Mockup Folder", clicked=self.select_mockup_folder))
        self.mockup_nav_label = QLabel("Mockup: Not Selected")
        sidebar.addWidget(self.mockup_nav_label)
        sidebar.addWidget(QPushButton("Prev Mockup", clicked=self.prev_mockup))
        sidebar.addWidget(QPushButton("Next Mockup", clicked=self.next_mockup))

        self.size_slider = self._add_slider(sidebar, "Size %", 10, 200, 100)
        self.opacity_slider = self._add_slider(sidebar, "Opacity %", 0, 100, 100)
        self.offset_x_slider = self._add_slider(sidebar, "Offset X", -500, 500, 0)
        self.offset_y_slider = self._add_slider(sidebar, "Offset Y", -500, 500, 0)

        self.aspect_ratio_checkbox = QCheckBox("Lock Aspect Ratio")
        self.aspect_ratio_checkbox.setChecked(True)
        sidebar.addWidget(self.aspect_ratio_checkbox)

        sidebar.addWidget(QPushButton("Update Preview", clicked=self.update_preview))
        sidebar.addWidget(QPushButton("Generate Mockup", clicked=self.generate_mockup))

    def _add_slider(self, layout, label_text, min_val, max_val, default):
        layout.addWidget(QLabel(label_text))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.valueChanged.connect(self.update_preview)
        layout.addWidget(slider)
        return slider

    def select_design_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Design Folder")
        if folder:
            self.design_folder = folder
            self.design_files = [f for f in os.listdir(folder) if f.lower().endswith(SUPPORTED_FORMATS)]
            self.current_design_index = 0
            self.update_preview()

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder")
        if folder:
            self.mockup_folder = folder
            self.mockup_files = [f for f in os.listdir(folder) if f.lower().endswith(SUPPORTED_FORMATS)]
            self.current_mockup_index = 0
            self.update_preview()

    def next_design(self):
        if self.design_files:
            self.current_design_index = (self.current_design_index + 1) % len(self.design_files)
            self.update_preview()

    def prev_design(self):
        if self.design_files:
            self.current_design_index = (self.current_design_index - 1) % len(self.design_files)
            self.update_preview()

    def next_mockup(self):
        if self.mockup_files:
            self.current_mockup_index = (self.current_mockup_index + 1) % len(self.mockup_files)
            self.update_preview()

    def prev_mockup(self):
        if self.mockup_files:
            self.current_mockup_index = (self.current_mockup_index - 1) % len(self.mockup_files)
            self.update_preview()

    def update_preview(self):
        if not self.design_files or not self.mockup_files:
            return

        design_path = os.path.join(self.design_folder, self.design_files[self.current_design_index])
        mockup_path = os.path.join(self.mockup_folder, self.mockup_files[self.current_mockup_index])
        self.design_nav_label.setText(f"Design: {os.path.basename(design_path)}")
        self.mockup_nav_label.setText(f"Mockup: {os.path.basename(mockup_path)}")

        try:
            mockup_img = Image.open(mockup_path).convert("RGBA")
            design_img = Image.open(design_path).convert("RGBA")

            scale = self.size_slider.value() / 100.0
            new_size = (int(design_img.width * scale), int(design_img.height * scale))
            design_img = design_img.resize(new_size, Image.LANCZOS)

            alpha = design_img.split()[3]
            alpha = alpha.point(lambda p: int(p * (self.opacity_slider.value() / 100)))
            design_img.putalpha(alpha)

            x = (mockup_img.width - design_img.width) // 2 + self.offset_x_slider.value()
            y = (mockup_img.height - design_img.height) // 2 + self.offset_y_slider.value()
            mockup_img.paste(design_img, (x, y), design_img)

            qimage = QImage(mockup_img.tobytes("raw", "RGBA"), mockup_img.width, mockup_img.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

            self.last_composited = mockup_img

        except Exception as e:
            self.preview_label.setText(f"[Preview Error]\n{e}")
            self.last_composited = None

    def generate_mockup(self):
        if not hasattr(self, 'last_composited') or self.last_composited is None:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"mockup_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)

        try:
            self.last_composited.save(output_path)
            self.statusBar().showMessage(f"Saved: {output_path}", 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Error saving file: {e}", 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddyApp()
    window.show()
    sys.exit(app.exec_())
