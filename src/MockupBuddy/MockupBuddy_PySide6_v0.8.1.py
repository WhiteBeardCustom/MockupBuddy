# MockupBuddy_PySide6_v0.6.6a
# ✅ Based on v0.6.5_FULL with restoration of all features and UI updates
# ✅ Authoritative working baseline for new iterations

import sys
import os
import re
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QSlider, QScrollArea, QTextEdit, QSizePolicy,
    QComboBox, QCheckBox, QProgressBar, QDialog
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PIL import Image, ImageQt
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QMessageBox
from collections import defaultdict
import platform
import webbrowser
import subprocess

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
    """
    Resolves the absolute path to an asset in a cross-platform way.
    - In development: loads from ../assets
    - In PyInstaller Windows/macOS: loads from sys._MEIPASS or bundle-relative
    """
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS  # Used by PyInstaller
        else:
            # Fallback to the executable's directory (common for macOS .app)
            base_path = os.path.dirname(sys.executable)
        asset_path = os.path.join(base_path, "assets", filename)
    else:
        # Development environment (source run)
        base_path = os.path.dirname(__file__)
        asset_path = os.path.abspath(os.path.join(base_path, "..", "assets", filename))

    print(f"[Asset Debug] Resolved asset path: {asset_path}")
    print(f"[Asset Debug] Exists? {os.path.exists(asset_path)}")
    return asset_path

def apply_opacity(image, opacity):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    alpha = image.getchannel('A').point(lambda p: int(p * opacity))
    image.putalpha(alpha)
    return image

def open_support_link():
    url = "https://www.buymeacoffee.com/nicktrautman"
    try:
        print(f"[Coffee Debug] Attempting to open URL: {url}")
        if sys.platform.startswith('win'):
            os.startfile(url)  # Native Windows method
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"Error opening support link: {e}")

def normalize_name(filename):
    name = os.path.splitext(os.path.basename(filename))[0].lower()
    name = re.sub(r'[\s\-]+', '_', name)  # Replace spaces and dashes with underscores
    name = re.sub(r'[^a-z0-9_]', '', name)  # Remove special characters
    return name

def is_light_design(filename):
    normalized = normalize_name(filename)
    return normalized.endswith('_light')

def is_dark_design(filename):
    normalized = normalize_name(filename)
    return normalized.endswith('_dark')

def get_design_basename(filename):
    base = normalize_name(filename)
    base = re.sub(r'_light$|_dark$', '', base)
    return base

# [File continues with full class implementation previously confirmed]

class MockupBuddy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PySide6 v0.8")
        self._initialize_window_size()
        self.config = load_config()
        self.templates = load_templates()

        # Folders from config (or empty)
        self.design_folder = self.config.get("design_folder", "")
        self.mockup_folder = self.config.get("mockup_folder", "")
        self.output_folder = self.config.get("output_folder", "")
        self.move_completed = self.config.get("move_completed", True)

        self.checkbox_vars = []

        self.init_ui()

        # 🔁 Restore folder paths and dropdowns on launch
        if self.design_folder:
            self.set_elided_text(self.design_label, self.design_folder)
            self.populate_dropdown(self.design_dropdown, self.design_folder)
        if self.mockup_folder:
            self.set_elided_text(self.mockup_label, self.mockup_folder)
            self.populate_dropdown(self.mockup_dropdown, self.mockup_folder)
        if self.output_folder:
            self.set_elided_text(self.output_label, self.output_folder)
        # Force preview placeholder on startup (even with preloaded config)
        QTimer.singleShot(0, lambda: self.preview_label.setText("🛑 Preview not available. Please reload Designs & Mockups."))
    
    def get_design_type(self, filename):
        name = filename.lower()
        if "dark" in name:
            return "dark"
        elif "light" in name:
            return "light"
        else:
            return "neutral"

    def calculate_new_size(self, image):
        size = self.size_slider.value()
        return size, size

    def _initialize_window_size(self):
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        screen_width = screen.width()
        screen_height = screen.height()
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.95)
        self.resize(window_width, window_height)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.move(x, y)


    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        import platform
        icon_filename = "MockupBuddyDesktop.icns" if platform.system() == "Darwin" else "MockupBuddyDesktop.ico"
        icon_path = get_asset_path(icon_filename)
        self.setWindowIcon(QIcon(icon_path))
        layout = QHBoxLayout(main_widget)

        # Left panel: scrollable controls
        control_scroll = QScrollArea()
        control_scroll.setWidgetResizable(True)
        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(10)
        control_scroll.setWidget(control_container)

        # Folder pickers
        self.reload_button = QPushButton("🔄 Reload Designs / Mockups")
        self.reload_button.setStyleSheet("background-color: #ffd966; font-weight: bold; padding: 6px; border: 1px solid #ccc;")
        self.reload_button.setToolTip("Reload Design & Mockup options from selected folders")
        self.reload_button.clicked.connect(self.reload_designs_and_mockups)
        control_layout.addWidget(self.reload_button)
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

        # Design & Mockup dropdowns
        self.design_dropdown = QComboBox()
        self.mockup_dropdown = QComboBox()
        self.design_dropdown.blockSignals(True)
        self.design_dropdown.currentIndexChanged.connect(self.on_design_changed)
        self.design_dropdown.blockSignals(False)
        self.mockup_dropdown.currentIndexChanged.connect(self.update_preview)

        control_layout.addWidget(QLabel("🎨 Select Design"))
        control_layout.addWidget(self.design_dropdown)
        

        # Mockup Template Scroll Container
        self.template_header = QLabel("🧩 Mockup Templates")
        control_layout.addWidget(self.template_header)

        self.template_scroll = QScrollArea()
        self.template_scroll.setWidgetResizable(True)
        self.template_widget = QWidget()
        self.template_layout = QVBoxLayout()
        self.template_widget.setLayout(self.template_layout)
        self.template_scroll.setWidget(self.template_widget)
        self.template_scroll.setFixedHeight(150)
        control_layout.addWidget(self.template_scroll)

        # Sliders and lock aspect toggle
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


        slider_container = QWidget()
        slider_layout = QVBoxLayout()
        slider_container.setLayout(slider_layout)
        
        from PySide6.QtWidgets import QLineEdit

        for label_text, slider in [
            ("Design Size", self.size_slider),
            ("Opacity", self.opacity_slider),
            ("X Offset", self.x_offset_slider),
            ("Y Offset", self.y_offset_slider)
        ]:
            label = QLabel(label_text)
            input_field = QLineEdit(str(slider.value()))
            input_field.setFixedWidth(50)

            # Sync slider ➜ input field
            slider.valueChanged.connect(lambda val, field=input_field: field.setText(str(val)))
            # Sync input field ➜ slider
            input_field.editingFinished.connect(lambda s=slider, f=input_field: s.setValue(int(f.text())))

            row_layout = QHBoxLayout()
            row_layout.addWidget(label)
            row_layout.addWidget(slider)
            row_layout.addWidget(input_field)

            row_widget = QWidget()
            row_widget.setLayout(row_layout)
            slider_layout.addWidget(row_widget)



        # Now add the whole block to the sidebar
        control_layout.addWidget(slider_container)


        # Generate + Completed toggle
        self.generate_button = QPushButton("🚀 Generate Mockups")
        self.generate_button.setStyleSheet("background-color: #6fa8dc; font-weight: bold; padding: 6px; border: 1px solid #ccc;")
        self.generate_button.clicked.connect(self.generate_mockups)
        control_layout.addWidget(self.generate_button)

        self.move_checkbox = QCheckBox("📁 Move used designs to 'Completed Designs'")
        self.move_checkbox.setChecked(self.move_completed)
        self.move_checkbox.stateChanged.connect(lambda: self.set_move_flag(self.move_checkbox.isChecked()))
        control_layout.addWidget(self.move_checkbox)


        control_layout.addStretch()

        # RIGHT: Preview Panel + Debug Log
        right_layout = QVBoxLayout()
        self.preview_label = QLabel("Mockup Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #222; color: white;")
        self.preview_label.setMinimumHeight(600)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # (Coffee button now moved into the dropdown container below)

        # Mockup dropdown now above preview label
        self.mockup_dropdown = QComboBox()
        self.mockup_dropdown.currentIndexChanged.connect(self.update_preview)
        self.mockup_dropdown.setVisible(False)  # Hidden until design is selected
 
        dropdown_container = QWidget()
        dropdown_layout = QHBoxLayout()
        dropdown_layout.setContentsMargins(0, 0, 0, 0)
        dropdown_layout.setAlignment(Qt.AlignLeft)
        dropdown_layout.setSpacing(5)
        dropdown_container.setLayout(dropdown_layout)
        dropdown_layout.addWidget(QLabel("🖼 Select Mockup Preview"))
        dropdown_layout.addWidget(self.mockup_dropdown)
        dropdown_layout.addStretch()
        print("[Coffee Debug] Attempting to resolve path to Buy Me a Coffee asset...")
        coffee_path = get_asset_path("bmcNT.png")
        print("[Coffee Debug] Resolved path:", coffee_path)
        print("[Coffee Debug] Exists?", os.path.exists(coffee_path))
        if not os.path.exists(coffee_path):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Asset Error", f"bmcNT.png not found at:\n{coffee_path}")
        if os.path.exists(coffee_path):
            coffee_pixmap = QPixmap(coffee_path).scaled(140, 39, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            coffee_btn = QPushButton()
            coffee_btn.setIcon(QIcon(coffee_pixmap))
            coffee_btn.setIconSize(coffee_pixmap.size())
            coffee_btn.setFixedSize(coffee_pixmap.size())
            coffee_btn.setCursor(Qt.PointingHandCursor)
            coffee_btn.setStyleSheet("border: none;")
            coffee_btn.clicked.connect(open_support_link)
            dropdown_layout.addWidget(coffee_btn)
 
        right_layout.addWidget(dropdown_container)
        right_layout.addWidget(self.preview_label, 5)

        self.debug_log = QTextEdit()
        self.debug_log.setReadOnly(True)
        self.debug_log.setMaximumHeight(120)
        self.debug_log.setVisible(False)

        self.debug_toggle = QCheckBox("Show Debug Log")
        self.debug_toggle.stateChanged.connect(lambda: self.debug_log.setVisible(self.debug_toggle.isChecked()))

        right_layout.addWidget(self.debug_toggle)
        right_layout.addWidget(self.debug_log)

        # Wrap up layout
        layout.addWidget(control_scroll, 2)
        layout.addLayout(right_layout, 5)

        control_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 🛑 Clear any existing preview and dropdowns at load
        self.preview_label.clear()
        self.preview_label.setText("🛑 Preview not available. Please reload Designs & Mockups.")
        self.design_dropdown.setCurrentIndex(-1)
        self.mockup_dropdown.clear()
        self.mockup_dropdown.setVisible(False)
        control_layout.setContentsMargins(10, 10, 10, 20)  # Add some bottom padding
        QTimer.singleShot(100, lambda: control_scroll.ensureVisible(0, 0))

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
            self.set_elided_text(self.design_label, folder)
            self.populate_dropdown(self.design_dropdown, folder)

    def select_mockup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mockup Folder", self.mockup_folder)
        if folder:
            self.mockup_folder = folder
            self.config["mockup_folder"] = folder
            save_config(self.config)
            self.set_elided_text(self.mockup_label, folder)
            self.populate_dropdown(self.mockup_dropdown, folder)

            self.populate_template_checkboxes()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.config["output_folder"] = folder
            save_config(self.config)
            self.set_elided_text(self.output_label, folder)

    def populate_dropdown(self, dropdown, folder):
        dropdown.clear()
        if not os.path.isdir(folder):
            return
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
        dropdown.addItems(files)
        
    def populate_mockup_dropdown(self):
        self.mockup_dropdown.clear()
        design_name = self.design_dropdown.currentText()
        if not design_name:
            return

        design_type = self.get_design_type(design_name)

        valid_files = []
        for file, checkbox, dark_toggle in self.checkbox_vars:
            is_dark = dark_toggle.isChecked()
            if (
                design_type == "neutral" or
                (design_type == "dark" and is_dark) or
                (design_type == "light" and not is_dark)
            ):
                valid_files.append(file)

        self.mockup_dropdown.addItems(valid_files)
        self.mockup_dropdown.setVisible(bool(valid_files))
        
    def on_design_changed(self):
        self.populate_mockup_dropdown()
        if not self.mockup_dropdown.count():
            return
        self.update_preview()


    def update_preview(self):
        if not (self.mockup_folder and self.design_folder):
            return

        design_name = self.design_dropdown.currentText()
        mockup_name = self.mockup_dropdown.currentText()

        if not (design_name and mockup_name):
            return

        design_type = "neutral"
        if is_dark_design(design_name):
            design_type = "dark"
        elif is_light_design(design_name):
            design_type = "light"

        is_dark_mockup = self.templates.get(mockup_name, {}).get("is_dark", False)

        # 🛑 Prevent mismatched preview attempts before rendering begins
        if (
            (design_type == "dark" and not is_dark_mockup) or
            (design_type == "light" and is_dark_mockup)
        ):
            self.preview_label.setText("⚠️ Incompatible Design and Mockup pairing.")
            self.log(f"⚠️ Skipped preview for {design_name} on {mockup_name} due to pairing rules.")
            return

        # ✅ Now safe to render preview
        design_path = os.path.join(self.design_folder, design_name)
        mockup_path = os.path.join(self.mockup_folder, mockup_name)

        try:
            mockup_img = Image.open(mockup_path).convert("RGBA")
            design_img = Image.open(design_path).convert("RGBA")
            new_w, new_h = self.calculate_new_size(design_img)

            design_img = design_img.resize((new_w, new_h), Image.LANCZOS)
            design_img = apply_opacity(design_img, self.opacity_slider.value() / 100.0)
            x = (mockup_img.width - new_w) // 2 + self.x_offset_slider.value()
            y = (mockup_img.height - new_h) // 2 + self.y_offset_slider.value()

            mockup_img.paste(design_img, (x, y), design_img)
            qt_img = QPixmap.fromImage(ImageQt.ImageQt(mockup_img))
            self.preview_label.setPixmap(qt_img.scaled(
                self.preview_label.width(), self.preview_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

            self.log(f"Preview: {design_name} + {mockup_name}")
        except Exception as e:
            self.log(f"Preview error: {e}")
    def set_elided_text(self, label, text, max_width=300):
        from PySide6.QtGui import QFontMetrics
        metrics = QFontMetrics(label.font())
        elided = metrics.elidedText(text, Qt.ElideMiddle, max_width)
        label.setText(elided)
        label.setToolTip(text)  # Optional: show full path on hover
    def populate_template_checkboxes(self):
        self.checkbox_vars.clear()
        for i in reversed(range(self.template_layout.count())):
            widget = self.template_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.mockup_folder:
            return

        files = sorted(f for f in os.listdir(self.mockup_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg')))
        for file in files:
            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(5, 2, 5, 2)

            checkbox = QCheckBox(file)
            checkbox.setChecked(True)

            dark_toggle = QCheckBox("Dark BG")
            dark_toggle.setChecked(self.templates.get(file, {}).get("is_dark", False))
            dark_toggle.stateChanged.connect(
                lambda _, f=file, chk=dark_toggle: self.update_dark_flag(f, chk.isChecked())
            )

            row_layout.addWidget(checkbox)
            row_layout.addStretch()
            row_layout.addWidget(dark_toggle)
            row.setLayout(row_layout)

            self.template_layout.addWidget(row)
            self.checkbox_vars.append((file, checkbox, dark_toggle))

    def update_dark_flag(self, filename, is_dark):
        if filename not in self.templates:
            self.templates[filename] = {}
        self.templates[filename]["is_dark"] = is_dark
        save_templates(self.templates)

    def reload_designs_and_mockups(self):
        if self.design_folder:
            self.populate_dropdown(self.design_dropdown, self.design_folder)
        if self.mockup_folder:
            self.populate_template_checkboxes()

        if self.design_dropdown.count() > 0:
            self.design_dropdown.setCurrentIndex(0)

        if self.mockup_dropdown.count() > 0:
            self.mockup_dropdown.setCurrentIndex(0)

        self.preview_label.setText("✅ Reloaded. Select a design to continue.")
        self.log("🔁 Designs and Mockups reloaded.")

        # Refresh mockup dropdown based on selected design
        self.populate_mockup_dropdown()

        if self.design_dropdown.currentText() and self.mockup_dropdown.currentText():
            self.update_preview()
    
    
    from collections import defaultdict

    def generate_mockups(self):
        all_files = sorted([f for f in os.listdir(self.design_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        design_groups = defaultdict(list)
        for f in all_files:
            base = get_design_basename(f)
            design_groups[base].append(f)

        popup = QDialog(self)
        popup.setWindowTitle("Generating Mockups")
        popup.setFixedSize(500, 160)
        layout = QVBoxLayout(popup)
        label = QLabel("Starting...")
        progress = QProgressBar()
        progress.setRange(0, len(design_groups))
        layout.addWidget(label)
        layout.addWidget(progress)
        popup.show()
        popup.raise_()
        popup.activateWindow()

        mockup_count = 0
        unique_basenames = set()

        for i, (base_name, variant_files) in enumerate(design_groups.items()):
            max_name_length = 35
            ellipsis = "..." if len(base_name) > max_name_length else ""
            truncated_base = base_name[:max_name_length] + ellipsis

            for variant in variant_files:
                label.setText(f"Creating mockups for {truncated_base} ({i + 1} of {len(design_groups)})\n→ Variant: {variant}")
                progress.setValue(i)
                popup.repaint()
                QApplication.processEvents()
                try:
                    design_path = os.path.join(self.design_folder, variant)
                    base = get_design_basename(variant)
                    design_is_dark = is_dark_design(variant)
                    design_is_light = is_light_design(variant)
                    design_type = "neutral"
                    if design_is_dark:
                        design_type = "dark"
                    elif design_is_light:
                        design_type = "light"

                    selected_mockups = [
                        (file, dark_toggle.isChecked())
                        for file, checkbox, dark_toggle in self.checkbox_vars
                        if checkbox.isChecked()
                    ]
                    self.log(f"🔍 Generating mockups for design_type={design_type}")

                    if not selected_mockups:
                        QMessageBox.warning(self, "No Mockups Selected", "Please check at least one mockup template.")
                        return

                    for mockup_file, is_dark in selected_mockups:
                        mockup_path = os.path.join(self.mockup_folder, mockup_file)
                        if not os.path.exists(mockup_path):
                            continue

                        mockup_img = Image.open(mockup_path).convert("RGBA")
                        self.log(f"🧩 Mockup template: {mockup_file}, is_dark={is_dark}")

                        if (
                            (design_type == "dark" and not is_dark) or
                            (design_type == "light" and is_dark)
                        ):
                            self.log(f"⏭ Skipped: {variant} → {mockup_file} (mismatch)")
                            continue
                        else:
                            self.log(f"✔ Matched: {variant} → {mockup_file} (ok)")

                        design_img = Image.open(design_path).convert("RGBA")
                        new_w, new_h = self.calculate_new_size(design_img)

                        overlay = design_img.resize((new_w, new_h), Image.LANCZOS)
                        overlay = apply_opacity(overlay, self.opacity_slider.value() / 100.0)
                        x = (mockup_img.width - new_w) // 2 + self.x_offset_slider.value()
                        y = (mockup_img.height - new_h) // 2 + self.y_offset_slider.value()
                        mockup_img.paste(overlay, (x, y), overlay)

                        sanitized_base = re.sub(r'\s+', '_', base.strip().lower())
                        color_part = mockup_file.replace(".png", "")
                        out_dir = os.path.join(self.output_folder, f"Mockups - {sanitized_base}")
                        os.makedirs(out_dir, exist_ok=True)
                        out_name = f"{sanitized_base}_{color_part}.png"
                        out_path = os.path.join(out_dir, out_name)
                        mockup_img.save(out_path)
                        self.log(f"✔ Saved: {out_name}")
                        mockup_count += 1
                        unique_basenames.add(base)

                    if self.move_completed:
                        completed_dir = os.path.join(self.design_folder, "Completed Designs")
                        os.makedirs(completed_dir, exist_ok=True)
                        os.rename(design_path, os.path.join(completed_dir, variant))

                except Exception as e:
                    self.log(f"Error with {variant}: {e}")

        progress.setValue(len(design_groups))
        label.setText(f"✅ {mockup_count} Mockups created for {len(unique_basenames)} Design(s).")
        close_button = QPushButton("Close")
        close_button.clicked.connect(popup.accept)
        layout.addWidget(close_button)
        popup.repaint()
        save_templates(self.templates)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockupBuddy()
    window.show()
    sys.exit(app.exec())