# MockupBuddy - PyQt Edition v0.4.7 Complete
# ✅ Based on v0.4.6 (preserves all functionality)
# ✅ Batch Mode: Apply one design to all mockups
# ✅ Output Summary: Designs processed, mockups generated
# ✅ Reset All Settings button
# ✅ Full folder path display
# ❌ Multiply blend mode removed

import sys, os, json
from datetime import datetime
from pathlib import Path
from io import BytesIO

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSlider, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image

CONFIG_PATH = os.path.expanduser("~/.mockupbuddy_config.json")

class MockupBuddy(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy v0.4.7")
        self.resize(1200, 800)

        self.design_folder = ""
        self.mockup_folder = ""
        self.output_folder = ""
        self.design_images = []
        self.mockup_images = []

        self.size = 50
        self.opacity = 100
        self.offset_x = 0
        self.offset_y = 0
        self.lock_aspect = True

        self.load_config()
        self.setup_ui()
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

        btn_reset = QPushButton("Reset All Settings")
        btn_reset.clicked.connect(self.reset_settings)

        controls.addWidget(self.design_label)
        controls.addWidget(btn_design)
        controls.addWidget(self.mockup_label)
        controls.addWidget(btn_mockup)
        controls.addWidget(self.output_label)
        controls.addWidget(btn_output)
        controls.addWidget(btn_reset)

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

        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray")

        btn_preview = QPushButton("Update Preview")
        btn_preview.clicked.connect(self.update_preview)

        btn_generate = QPushButton("Generate Mockups")
        btn_generate.clicked.connect(self.generate_batch)

        controls.addWidget(btn_preview)
        controls.addWidget(btn_generate)

        layout.addLayout(controls, 1)
        layout.addWidget(self.preview_label, 3)

    def create_slider(self, label_text, min_val, max_val, init_val, callback):
        box = QWidget()
        layout = QVBoxLayout()
        label = QLabel(label_text)
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(init_val)
        slider.valueChanged.connect(callback)
        layout.addWidget(label)
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

    def reset_settings(self):
        self.design_folder = ""
        self.mockup_folder = ""
        self.output_folder = ""
        self.size = 50
        self.opacity = 100
        self.offset_x = 0
        self.offset_y = 0
        self.save_config()
        QMessageBox.information(self, "Reset", "All settings have been cleared. Please restart the app.")
        self.close()

    def load_images(self):
        self.design_images = []
        self.mockup_images = []
        if os.path.exists(self.design_folder):
            self.design_images = [f for f in os.listdir(self.design_folder) if f.lower().endswith((".png", ".jpg"))]
        if os.path.exists(self.mockup_folder):
            self.mockup_images = [f for f in os.listdir(self.mockup_folder) if f.lower().endswith((".png", ".jpg"))]
        self.update_preview()

    def overlay_design(self, mockup, design):
        design = design.convert("RGBA")
        scale = self.size / 100.0
        new_size = (int(design.width * scale), int(design.height * scale))
        design = design.resize(new_size, Image.LANCZOS)
        alpha = design.split()[3].point(lambda p: int(p * (self.opacity / 100)))
        design.putalpha(alpha)
        overlay = Image.new("RGBA", mockup.size, (0, 0, 0, 0))
        x = (mockup.width - design.width) // 2 + self.offset_x
        y = (mockup.height - design.height) // 2 + self.offset_y
        overlay.paste(design, (x, y), design)
        return Image.alpha_composite(mockup.convert("RGBA"), overlay)

    def update_preview(self):
        try:
            if not self.design_images or not self.mockup_images:
                self.preview_label.setText("Missing design or mockup.")
                return
            design = Image.open(os.path.join(self.design_folder, self.design_images[0]))
            mockup = Image.open(os.path.join(self.mockup_folder, self.mockup_images[0]))
            result = self.overlay_design(mockup, design)
            buffer = BytesIO()
            result.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio))
        except Exception as e:
            print(f"[Preview Error] {e}")

    def generate_batch(self):
        try:
            total_created = 0
            print("Starting batch generation...")
            for design_file in self.design_images:
                design_path = os.path.join(self.design_folder, design_file)
                print(f"Opening design: {design_path}")
                design = Image.open(design_path)
                for mockup_file in self.mockup_images:
                    mockup_path = os.path.join(self.mockup_folder, mockup_file)
                    print(f"Opening mockup: {mockup_path}")
                    mockup = Image.open(mockup_path)
                    result = self.overlay_design(mockup, design)
                    name = f"{Path(design_file).stem}_{Path(mockup_file).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    out_path = os.path.join(self.output_folder, name)
                    print(f"Saving mockup to: {out_path}")
                    result.save(out_path)
                    total_created += 1

            print(f"Generated {total_created} mockups.")
            QMessageBox.information(
                self,
                "Batch Complete",
                f"Processed {len(self.design_images)} design(s)\nGenerated {total_created} mockup(s)."
            )

        except Exception as e:
            print(f"[Batch Error] {e}")
            QMessageBox.warning(self, "Error", str(e))

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "design_folder": self.design_folder,
                "mockup_folder": self.mockup_folder,
                "output_folder": self.output_folder
            }, f)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                self.design_folder = config.get("design_folder", "")
                self.mockup_folder = config.get("mockup_folder", "")
                self.output_folder = config.get("output_folder", "")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MockupBuddy()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        with open("mockupbuddy_crashlog.txt", "w") as f:
            f.write(traceback.format_exc())
        print("[FATAL ERROR] See mockupbuddy_crashlog.txt")
