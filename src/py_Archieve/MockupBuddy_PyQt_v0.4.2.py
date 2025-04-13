# MockupBuddy - PyQt Edition v0.4.2
# ✅ Fixed: Folder validation and file list checks
# ✅ Fixed: Index out of range errors on preview
# ✅ Fixed: PIL.ImageQt import now works
# ✅ Safe Preview and Generate logic

import sys, os, json
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QSlider, QCheckBox, QGroupBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image, ImageChops
from PIL.ImageQt import ImageQt

CONFIG_PATH = os.path.expanduser("~/.mockupbuddy_config.json")

class MockupBuddy(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PyQt Edition")
        self.resize(1200, 800)

        self.design_folder = ""
        self.mockup_folder = ""
        self.output_folder = ""
        self.design_images = []
        self.mockup_images = []
        self.current_design_index = 0
        self.current_mockup_index = 0

        self.size = 50
        self.opacity = 100
        self.offset_x = 0
        self.offset_y = 0
        self.lock_aspect = True
        self.use_multiply = False
        self.move_completed = False

        self.load_config()
        self.setup_ui()

        if self.design_folder and self.mockup_folder:
            self.load_images()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        controls = QVBoxLayout()

        self.design_label = QLabel(f"Design Folder: {self.design_folder}")
        btn_design = QPushButton("Select Design Folder")
        btn_design.clicked.connect(self.select_design_folder)

        self.mockup_label = QLabel(f"Mockup Folder: {self.mockup_folder}")
        btn_mockup = QPushButton("Select Mockup Folder")
        btn_mockup.clicked.connect(self.select_mockup_folder)

        self.output_label = QLabel(f"Output Folder: {self.output_folder}")
        btn_output = QPushButton("Select Output Folder")
        btn_output.clicked.connect(self.select_output_folder)

        controls.addWidget(self.design_label)
        controls.addWidget(btn_design)
        controls.addWidget(self.mockup_label)
        controls.addWidget(btn_mockup)
        controls.addWidget(self.output_label)
        controls.addWidget(btn_output)

        self.size_slider = self.create_slider("Size %", 1, 100, self.size, self.set_size)
        self.opacity_slider = self.create_slider("Opacity %", 0, 100, self.opacity, self.set_opacity)
        self.offset_x_slider = self.create_slider("Offset X", -200, 200, self.offset_x, self.set_offset_x)
        self.offset_y_slider = self.create_slider("Offset Y", -200, 200, self.offset_y, self.set_offset_y)

        controls.addWidget(self.size_slider)
        controls.addWidget(self.opacity_slider)
        controls.addWidget(self.offset_x_slider)
        controls.addWidget(self.offset_y_slider)

        self.chk_aspect = QCheckBox("Lock Aspect Ratio")
        self.chk_aspect.setChecked(True)
        self.chk_aspect.stateChanged.connect(lambda: setattr(self, "lock_aspect", self.chk_aspect.isChecked()))
        controls.addWidget(self.chk_aspect)

        self.chk_multiply = QCheckBox("Use Multiply Blend Mode")
        self.chk_multiply.stateChanged.connect(lambda: setattr(self, "use_multiply", self.chk_multiply.isChecked()))
        controls.addWidget(self.chk_multiply)

        self.chk_move = QCheckBox("Move to Completed Designs")
        self.chk_move.stateChanged.connect(lambda: setattr(self, "move_completed", self.chk_move.isChecked()))
        controls.addWidget(self.chk_move)

        btn_preview = QPushButton("Update Preview")
        btn_preview.clicked.connect(self.update_preview)
        btn_generate = QPushButton("Generate Mockup")
        btn_generate.clicked.connect(self.generate_mockup)
        controls.addWidget(btn_preview)
        controls.addWidget(btn_generate)

        self.preview_label = QLabel("Preview will show here")
        self.preview_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(controls, 1)
        layout.addWidget(self.preview_label, 3)

    def create_slider(self, label_text, min_val, max_val, init_val, callback):
        box = QGroupBox(label_text)
        layout = QVBoxLayout()
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(init_val)
        slider.valueChanged.connect(callback)
        layout.addWidget(slider)
        box.setLayout(layout)
        return box

    def set_size(self, val): self.size = val; self.update_preview()
    def set_opacity(self, val): self.opacity = val; self.update_preview()
    def set_offset_x(self, val): self.offset_x = val; self.update_preview()
    def set_offset_y(self, val): self.offset_y = val; self.update_preview()

    def select_design_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Design Folder")
        if path:
            self.design_folder = path
            self.design_label.setText(f"Design Folder: {path}")
            self.load_images()
            self.save_config()

    def select_mockup_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Mockup Folder")
        if path:
            self.mockup_folder = path
            self.mockup_label.setText(f"Mockup Folder: {path}")
            self.load_images()
            self.save_config()

    def select_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_folder = path
            self.output_label.setText(f"Output Folder: {path}")
            self.save_config()

    def load_images(self):
        if self.design_folder:
            self.design_images = [f for f in os.listdir(self.design_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            self.current_design_index = 0
        if self.mockup_folder:
            self.mockup_images = [f for f in os.listdir(self.mockup_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            self.current_mockup_index = 0
        if self.design_images and self.mockup_images:
            self.update_preview()

    def update_preview(self):
        try:
            if not self.design_images or not self.mockup_images:
                self.preview_label.setText("No images to preview.")
                return

            d_path = os.path.join(self.design_folder, self.design_images[self.current_design_index])
            m_path = os.path.join(self.mockup_folder, self.mockup_images[self.current_mockup_index])
            design = Image.open(d_path).convert("RGBA")
            mockup = Image.open(m_path).convert("RGBA")
            result = self.overlay_design(mockup, design)
            qt_img = ImageQt(result)
            pixmap = QPixmap.fromImage(qt_img)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio))
        except Exception as e:
            print(f"[Preview Error] {e}")
            self.preview_label.setText("Error loading preview")

    def overlay_design(self, mockup, design):
        w, h = design.size
        scale = self.size / 100.0
        new_size = (int(w * scale), int(h * scale))
        design = design.resize(new_size, Image.LANCZOS)
        if not self.use_multiply:
            alpha = design.split()[3]
            alpha = alpha.point(lambda p: int(p * (self.opacity / 100)))
            design.putalpha(alpha)
        x = (mockup.width - design.width) // 2 + self.offset_x
        y = (mockup.height - design.height) // 2 + self.offset_y
        if self.use_multiply:
            overlay = Image.new("RGBA", mockup.size, (0,0,0,0))
            overlay.paste(design, (x, y), design)
            return ImageChops.multiply(mockup, overlay)
        else:
            mockup.paste(design, (x, y), design)
            return mockup

    def generate_mockup(self):
        try:
            if not self.design_images or not self.mockup_images:
                print("[Generate Error] Missing files.")
                return

            d_path = os.path.join(self.design_folder, self.design_images[self.current_design_index])
            m_path = os.path.join(self.mockup_folder, self.mockup_images[self.current_mockup_index])
            design = Image.open(d_path).convert("RGBA")
            mockup = Image.open(m_path).convert("RGBA")
            result = self.overlay_design(mockup, design)
            name = f"{Path(d_path).stem}_{Path(m_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            out_path = os.path.join(self.output_folder or os.getcwd(), name)
            result.save(out_path)
            print(f"[Saved] {out_path}")
        except Exception as e:
            print(f"[Generate Error] {e}")

    def save_config(self):
        data = {
            "design_folder": self.design_folder,
            "mockup_folder": self.mockup_folder,
            "output_folder": self.output_folder
        }
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[Save Config Error] {e}")

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                self.design_folder = data.get("design_folder", "")
                self.mockup_folder = data.get("mockup_folder", "")
                self.output_folder = data.get("output_folder", "")
            except Exception as e:
                print(f"[Load Config Error] {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MockupBuddy()
    win.show()
    sys.exit(app.exec_())
