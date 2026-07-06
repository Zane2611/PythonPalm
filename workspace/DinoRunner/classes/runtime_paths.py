from pathlib import Path
import sys


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS).joinpath(*parts)
    return app_root().joinpath(*parts)