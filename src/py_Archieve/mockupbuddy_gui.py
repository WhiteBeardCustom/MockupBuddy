import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QSpinBox, QCheckBox, QGroupBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MockupBuddyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MockupBuddy - PyQt Edition")
        self.resize(int(0.95 * self.screen().size().width()), int(0.95 * self.screen().size().height()))
        self.init_ui()

    def init_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Sidebar Controls
        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar, 1)

        # Folder Selectors
        self.design_label = QLabel("Design Folder: Not Selected")
        self.mockup_label = QLabel("Mockup Folder: Not Selected")
        self.output_label = QLabel("Output Folder: Not Selected")

        sidebar.addWidget(self.design_label)
        sidebar.addWidget(QPushButton("Select Design Folder", clicked=self.select_design_folder))
        sidebar.addWidget(self.mockup_label)
        sidebar.addWidget(QPushButton("Select Mockup Folder", clicked=self.select_mockup_folder))
        sidebar.addWidget(self.output_label)
        sidebar.addWidget(QPushButton("Select Output Folder", clicked=self.select_output_folder))

        # Sliders Group
        slider_group = QGroupBox("Design Settings")
        slider_layout = QVBoxLayout()
        slider_group.setLayout(slider_layout)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(10)
        self.size_slider.setMaximum(300)
        self.size_slider.setValue(100)
        slider_layout.addWidget(QLabel("Size %"))
        slider_layout.addWidget(self.size_slider)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        slider_layout.addWidget(QLabel("Opacity %"))
        slider_layout.addWidget(self.opacity_slider)

        self.offset_x_slider = QSlider(Qt.Horizontal)
        self.offset_x_slider.setMinimum(-300)
        self.offset_x_slider.setMaximum(300)
        self.offset_x_slider.setValue(0)
        slider_layout.addWidget(QLabel("Offset X"))
        slider_layout.addWidget(self.offset_x_slider)

        self.offset_y_slider = QSlider(Qt.Horizontal)
        self.offset_y_slider.setMinimum(-300)
        self.offset_y_slider.setMaximum(300)
        self.offset_y_slider.setValue(0)
        slider_layout.addWidget(QLabel("Offset Y"))
        slider_layout.addWidget(self.offset_y_slider)

        self.aspect_ratio_checkbox = QCheckBox("Lock Aspect Ratio")
        self.aspect_ratio_checkbox.setChecked(True)
        slider_layout.addWidget(self.aspect_ratio_checkbox)

        sidebar.addWidget(slider_group)

        # Placeholder for Generate Button
        self.generate_btn = QPushButton("Generate Mockups")
        sidebar.addWidget(self.generate_btn)

        # Preview Area
        self.preview_label = QLabel("Preview will show here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #333; color: white;")
        main_layout.addWidget(self.preview_label, 2)

    def select_design_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Design Folder")
        if path:
            self.design_label.setText(f"Design Folder: {path}")

    def select_mockup_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Mockup Folder")
        if path:
            self.mockup_label.setText(f"Mockup Folder: {path}")

    def select_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_label.setText(f"Output Folder: {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupBuddyApp()
    window.show()
    sys.exit(app.exec_())
