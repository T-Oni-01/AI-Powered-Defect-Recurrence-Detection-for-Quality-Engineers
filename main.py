import sys
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    torch_lib_path = os.path.join(base_path, 'torch', 'lib')
    if os.path.exists(torch_lib_path):
        os.environ['PATH'] = torch_lib_path + os.pathsep + os.environ.get('PATH', '')

try:
    import torch
    print(f"PyTorch {torch.__version__} loaded successfully")
except Exception as e:
    print(f"Warning: PyTorch loading issue: {e}")

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.theme_manager import apply_light, apply_dark


def main():
    app = QApplication(sys.argv)

    apply_light(app)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()