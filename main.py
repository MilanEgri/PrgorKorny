import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QFileDialog, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect,
    QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt
from PIL import Image


class ImageCompressorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Compressor Pro")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        self.current_image_path = None

        # === Central Widget & Layout ===
        central = QWidget()
        central.setStyleSheet("background-color: #0d1117;")  # GitHub dark background
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(60, 60, 60, 60)
        main_layout.setSpacing(30)

        # === Title ===
        title = QLabel("Image Compressor Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #c9d1d9;")  # GitHub light text
        main_layout.addWidget(title)

        # === Description ===
        desc = QLabel(
            "• Load or change an image with the button below.\n"
            "• Compress the image and save.\n"
            "• Use “Close” to exit the application at any time."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setFont(QFont("Segoe UI", 16))
        desc.setStyleSheet("color: #8b949e;")  # GitHub muted text
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        # === Image Frame with Drop Shadow ===
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #161b22;  /* GitHub card background */
                border-radius: 16px;
            }
            """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 150))
        frame.setGraphicsEffect(shadow)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)

        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        self.image_label.setStyleSheet("color: #8b949e;")  # muted placeholder text
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_layout.addWidget(self.image_label)

        main_layout.addWidget(frame, stretch=1)

        # === Button Bar ===
        btn_bar = QWidget()
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(40)

        self.load_btn = QPushButton("Load Image")
        self._style_button(self.load_btn)
        self.load_btn.clicked.connect(self.load_image)
        btn_layout.addWidget(self.load_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.compress_btn = QPushButton("Compress & Save")
        self._style_button(self.compress_btn)
        self.compress_btn.clicked.connect(self.compress_and_save_image)
        btn_layout.addWidget(self.compress_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.close_btn = QPushButton("Close")
        self._style_button(self.close_btn)
        self.close_btn.clicked.connect(self.close_app)
        btn_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addWidget(btn_bar)

        self.setCentralWidget(central)
        self.image_frame = frame

    def _style_button(self, btn: QPushButton):
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 14))
        btn.setFixedHeight(50)
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #21262d;  /* GitHub button background */
                color: #c9d1d9;             /* GitHub button text */
                border: none;
                border-radius: 12px;
                padding-left: 24px;
                padding-right: 24px;
            }
            QPushButton:hover {
                background-color: #2d333b;  /* GitHub button hover */
            }
            QPushButton:pressed {
                background-color: #1b1f24;  /* GitHub button pressed */
            }
            """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 100))
        btn.setGraphicsEffect(shadow)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select an image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if not path:
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._show_message("Error", "Selected file is not a valid image.")
            return

        self.current_image_path = path
        self.load_btn.setText("Change Image")

        frame_rect = self.image_frame.contentsRect()
        max_w = frame_rect.width() - 40
        max_h = frame_rect.height() - 40
        scaled = pixmap.scaled(
            max_w, max_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setStyleSheet("")

    def compress_and_save_image(self):
        if not self.current_image_path:
            self._show_message("No Image", "First load an image using the button above.")
            return

        try:
            pil_img = Image.open(self.current_image_path)
        except Exception as e:
            self._show_message("Error", f"Failed to open image: {e}")
            return

        original_name = os.path.basename(self.current_image_path)
        name, _ = os.path.splitext(original_name)
        suggested_name = f"{name}_compressed.jpg"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            suggested_name,
            "JPEG Images (*.jpg *.jpeg);;PNG Images (*.png);;All Files (*)"
        )
        if not save_path:
            return

        save_ext = os.path.splitext(save_path)[1].lower()
        try:
            if save_ext in [".jpg", ".jpeg"]:
                pil_img.convert("RGB").save(save_path, "JPEG", quality=75)
            else:
                pil_img.save(save_path, "PNG", optimize=True, compress_level=6)
        except Exception as e:
            self._show_message("Error", f"Failed to save image: {e}")
            return

        self._show_message("Done", f"Image successfully saved to:\n{save_path}")

    def close_app(self):
        self.close()

    def _show_message(self, title: str, text: str):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        icon = QMessageBox.Icon.Information if title in ("Done", "No Image") else QMessageBox.Icon.Critical
        msg.setIcon(icon)
        msg.setStyleSheet(
            """
            QMessageBox {
                background-color: #0d1117; 
                color: #c9d1d9; 
                border: none;
            }
            QMessageBox QLabel {
                color: #c9d1d9;
            }
            QMessageBox QPushButton {
                background-color: #21262d; 
                color: #c9d1d9; 
                border-radius: 8px;
                padding: 6px 12px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2d333b;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1b1f24;
            }
            """
        )
        msg.exec()


if __name__ == "__main__":
    # Requirements:
    # pip install PyQt6 pillow

    app = QApplication(sys.argv)
    window = ImageCompressorApp()
    window.show()
    sys.exit(app.exec())
