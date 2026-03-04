# core/path_utils.py
import sys
import os


def get_base_path():
    """Get the base path - works for both script and exe"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys._MEIPASS
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_path(relative_path):
    """Get absolute path to data file"""
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)


def get_reports_path():
    """Get path for reports folder (create if needed)"""
    if getattr(sys, 'frozen', False):
        # When running as exe, save reports next to the exe
        base = os.path.dirname(sys.executable)
    else:
        # When running as script
        base = os.getcwd()

    reports_path = os.path.join(base, 'reports')
    os.makedirs(reports_path, exist_ok=True)
    return reports_path