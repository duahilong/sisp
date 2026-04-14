"""
Sisp 测试包
包含所有模块的单元测试
"""

import os
import sys


def _configure_utf8_console() -> None:
    """尽量将测试进程输出统一为 UTF-8，减少 Windows 终端乱码。"""
    try:
        os.environ.setdefault("PYTHONUTF8", "1")
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    except Exception:
        pass

    # Python 3.7+ 支持 reconfigure
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # Windows 控制台代码页切到 UTF-8
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass


_configure_utf8_console()

__version__ = "1.0.0"
