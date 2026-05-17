import os
import sys


def _get_project_roots():
    """Return the project root and the source root for normal execution."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_root = os.path.join(project_root, "src")
    return project_root, src_root


def get_resource_path(relative_path: str) -> str:
    """Resolve a relative resource path for normal execution and PyInstaller bundles."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    project_root, src_root = _get_project_roots()
    candidate = os.path.join(project_root, relative_path)
    if os.path.exists(candidate):
        return candidate

    return os.path.join(src_root, relative_path)


def get_config_load_path(config_file: str = "config.json") -> str:
    """Return the config path to load from, preferring local config next to the exe when bundled."""
    if hasattr(sys, "_MEIPASS"):
        exe_dir = os.path.dirname(sys.executable)
        local_config = os.path.join(exe_dir, config_file)
        if os.path.exists(local_config):
            return local_config
        return os.path.join(sys._MEIPASS, config_file)

    if os.path.isabs(config_file):
        return config_file

    project_root, _ = _get_project_roots()
    return os.path.join(project_root, config_file)


def get_config_save_path(config_file: str = "config.json") -> str:
    """Return a writable config save path for normal execution and bundled executables."""
    if hasattr(sys, "_MEIPASS"):
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, config_file)

    if os.path.isabs(config_file):
        return config_file

    project_root, _ = _get_project_roots()
    return os.path.join(project_root, config_file)
