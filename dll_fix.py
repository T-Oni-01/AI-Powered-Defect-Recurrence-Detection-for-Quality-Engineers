import os
import sys
import ctypes

def fix_dll_loading():

    if not getattr(sys, "frozen", False):
        return

    base_path = getattr(sys, "_MEIPASS", None)
    if not base_path:
        return

    torch_lib = os.path.join(base_path, "torch", "lib")
    if not os.path.isdir(torch_lib):
        return

    # 1) Modern + safest: add an explicit DLL directory (Python 3.8+)
    try:
        os.add_dll_directory(torch_lib)
    except Exception:
        pass

    # 2) Keep PATH as a fallback for downstream DLL resolution
    os.environ["PATH"] = torch_lib + os.pathsep + os.environ.get("PATH", "")

    # 3) Optional: try preloading a couple of common torch deps
    for dll in ("c10.dll", "torch_cpu.dll"):
        p = os.path.join(torch_lib, dll)
        if os.path.exists(p):
            try:
                ctypes.CDLL(p)
            except Exception:
                pass