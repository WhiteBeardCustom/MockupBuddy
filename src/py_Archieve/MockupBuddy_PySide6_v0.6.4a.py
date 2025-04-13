import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSlider, QScrollArea, QTextEdit, QSizePolicy,
    QComboBox, QCheckBox, QProgressBar, QDialog, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PIL import Image, ImageQt

CONFIG_PATH = os.path.expanduser("~/.wbmockup_config.json")
TEMPLATES_PATH = os.path.expanduser("~/.wbmockup_templates.json")

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

def load_templates():
    if os.path.exists(TEMPLATES_PATH):
        try:
            return json.load(open(TEMPLATES_PATH))
        except:
            pass
    return {}

def save_templates(templates):
    with open(TEMPLATES_PATH, 'w') as f:
        json.dump(templates, f)

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

def is_light_design(filename):
    return any(tag in filename.lower() for tag in ['_light', '-light'])

def is_dark_design(filename):
    return any(tag in filename.lower() for tag in ['_dark', '-dark'])

def get_design_basename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    for suffix in ['_light', '-light', '_dark', '-dark']:
        if base.lower().endswith(suffix):
            return base[:-len(suffix)]
    return base
class MockupBuddy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PySide6 v0.6.4a")
        self.resize(1200, 800)

        self.config = load_config()
        self.templates = load_templates()
        self.design_folder = self.config.get("design_folder", "")
        self.mockup_folder = self.config.get("mockup_folder", "")
        self.output_folder = self.config.get("output_folder", "")
        self.move_completed = self.config.get("move_completed", True)

        self.checkbox_vars = []  # [(mockup_name, checkbox_var, dark_tag_var)]
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # LEFT PANEL
        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(12)
        control_scroll.setWidget(control_container)

        # FOLDER PICKERS
        self.design_button = QPushButton("📂 Select Design Folder")
        self.mockup_button = QPushButton("🎨 Select Mockup Folder")
        self.output_button = QPushButton("💾 Select Output Folder")

        self.design_button.clicked.connect(self.select_design_folder)
        self.mockup_button.clicked.connect(self.select_mockup_folder)
        self.output_button.clicked.connect(self.select_output_folder)

        self.design_label = QLabel("(No folder selected)")
        self.mockup_label = QLabel("(No folder selected)")
        self.output_label = QLabel("(No folder selected)")

        control_layout.addWidget(self.design_button)
        control_layout.addWidget(self.design_label)
        control_layout.addWidget(self.mockup_button)
        control_layout.addWidget(self.mockup_label)
        control_layout.addWidget(self.output_button)
        control_layout.addWidget(self.output_label)
        # DESIGN + MOCKUP DROPDOWNS
        self.design_dropdown = QComboBox()
        self.mockup_dropdown = QComboBox()
        self.design_dropdown.currentIndexChanged.connect(self.update_preview)
        self.mockup_dropdown.currentIndexChanged.connect(self.update_preview)
        control_layout.addWidget(QLabel("Select Design"))
        control_layout.addWidget(self.design_dropdown)
        control_layout.addWidget(QLabel("Select Mockup (Preview Only)"))
        control_layout.addWidget(self.mockup_dropdown)

        # SLIDERS + TOGGLES
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(50, 1000)
        self.size_slider.setValue(400)
        self.size_slider.valueChanged.connect(self.update_preview)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_preview)

        self.x_offset_slider = QSlider(Qt.Horizontal)
        self.x_offset_slider.setRange(-500, 500)
        self.x_offset_slider.setValue(0)
        self.x_offset_slider.valueChanged.connect(self.update_preview)

        self.y_offset_slider = QSlider(Qt.Horizontal)
        self.y_offset_slider.setRange(-500, 500)
        self.y_offset_slider.setValue(0)
        self.y_offset_slider.valueChanged.connect(self.update_preview)

        self.lock_aspect_checkbox = QCheckBox("Lock Aspect Ratio")
        self.lock_aspect_checkbox.setChecked(True)
        self.lock_aspect_checkbox.stateChanged.connect(self.update_preview)

        for label, widget in [
            ("Design Size", self.size_slider),
            ("Opacity", self.opacity_slider),
            ("X Offset", self.x_offset_slider),
            ("Y Offset", self.y_offset_slider)
        ]:
            control_layout.addWidget(QLabel(label))
            control_layout.addWidget(widget)

        control_layout.addWidget(self.lock_aspect_checkbox)

        # GENERATE + TOGGLE
        self.generate_button = QPushButton("🚀 Generate Mockups")
        self.generate_button.clicked.connect(self.generate_mockups)
        control_layout.addWidget(self.generate_button)

        self.move_checkbox = QCheckBox("Move processed to Completed Designs")
        self.move_checkbox.setChecked(self.move_completed)
        self.move_checkbox.stateChanged.connect(lambda: self.set_move_flag(self.move_checkbox.isChecked()))
        control_layout.addWidget(self.move_checkbox)

        # COFFEE BUTTON
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

        # PREVIEW PANEL + DEBUG
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
    def set_move_flag(self, value):
        self.move_completed = value
        self.config["move_completed"] = value
        save_config(self.config)

    def log(self, message):
        self.debug_log.append(message)

    def select_design_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Design Folder", self.design_folder)
        if folder:
            self.design_folder = folder
            self.config["design_folder"] = folder
            save_config(self.config)
            self.design_label.setText(folder)
            self.populate_dropdown(self.design_dropdown, folder)
            self.refresh_mockup_checkboxes()

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder", self.mockup_folder)
        if folder:
            self.mockup_folder = folder
            self.config["mockup_folder"] = folder
            save_config(self.config)
            self.mockup_label.setText(folder)
            self.populate_dropdown(self.mockup_dropdown, folder)
            self.refresh_mockup_checkboxes()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.config["output_folder"] = folder
            save_config(self.config)
            self.output_label.setText(folder)

    def populate_dropdown(self, dropdown, folder):
        dropdown.clear()
        if not os.path.isdir(folder):
            return
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
        dropdown.addItems(files)

    def refresh_mockup_checkboxes(self):
        self.checkbox_vars = []
        if not os.path.isdir(self.mockup_folder):
            return
        for file in sorted(os.listdir(self.mockup_folder)):
            if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            is_dark = self.templates.get(file, {}).get("is_dark", False)
            var = QCheckBox(file)
            var.setChecked(True)
            dark_toggle = QCheckBox("Dark BG")
            dark_toggle.setChecked(is_dark)
            dark_toggle.stateChanged.connect(lambda state, f=file, v=dark_toggle: self.templates.update({f: {"is_dark": v.isChecked()}}))
            self.checkbox_vars.append((file, var, dark_toggle))

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
        designs = sorted([f for f in os.listdir(self.design_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        popup = QDialog(self)
        popup.setWindowTitle("Generating Mockups")
        popup.setFixedSize(400, 150)
        layout = QVBoxLayout(popup)
        label = QLabel("Starting...")
        progress = QProgressBar()
        progress.setRange(0, len(designs))
        layout.addWidget(label)
        layout.addWidget(progress)
        popup.show()

        for i, design_file in enumerate(designs):
            label.setText(f"Processing: {design_file}")
            progress.setValue(i)
            popup.repaint()
            try:
                design_path = os.path.join(self.design_folder, design_file)
                design_img = Image.open(design_path).convert("RGBA")
                base = get_design_basename(design_file)
                design_type = 'neutral'
                if is_dark_design(design_file):
                    design_type = 'dark'
                elif is_light_design(design_file):
                    design_type = 'light'

                for mockup_file, check, dark_check in self.checkbox_vars:
                    if not check.isChecked():
                        continue
                    is_dark = dark_check.isChecked()
                    if (design_type == "dark" and not is_dark) or (design_type == "light" and is_dark):
                        continue
                    mockup_path = os.path.join(self.mockup_folder, mockup_file)
                    mockup_img = Image.open(mockup_path).convert("RGBA")

                    w, h = design_img.size
                    if self.lock_aspect_checkbox.isChecked():
                        scale = self.size_slider.value() / max(w, h)
                        new_w, new_h = int(w * scale), int(h * scale)
                    else:
                        new_w = new_h = self.size_slider.value()

                    overlay = design_img.resize((new_w, new_h), Image.LANCZOS)
                    overlay = apply_opacity(overlay, self.opacity_slider.value() / 100.0)
                    x = (mockup_img.width - new_w) // 2 + self.x_offset_slider.value()
                    y = (mockup_img.height - new_h) // 2 + self.y_offset_slider.value()
                    mockup_img.paste(overlay, (x, y), overlay)

                    out_dir = os.path.join(self.output_folder, base)
                    os.makedirs(out_dir, exist_ok=True)
                    out_name = f"{base}_{os.path.splitext(mockup_file)[0]}.png"
                    out_path = os.path.join(out_dir, out_name)
                    mockup_img.save(out_path)
                    self.log(f"✔ Saved: {out_name}")

                if self.move_completed:
                    completed_dir = os.path.join(self.design_folder, "Completed Designs")
                    os.makedirs(completed_dir, exist_ok=True)
                    os.rename(design_path, os.path.join(completed_dir, design_file))

            except Exception as e:
                self.log(f"Error with {design_file}: {e}")

        progress.setValue(len(designs))
        label.setText("✅ Mockups generated.")
        popup.repaint()
        save_templates(self.templates)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddy()
    window.show()
    sys.exit(app.exec())