import pathlib
import platform


HOME = pathlib.Path.home()


def get_shared_data_directory(app_name: str) -> pathlib.Path:
    if platform.system() == "Windows":
        data_dir = HOME / "AppData" / "Local" / app_name
    elif platform.system() == "Darwin":
        data_dir = HOME / "Library" / "Application Support" / app_name
    else:  # Linux and other Unix-like systems
        data_dir = HOME / ".local" / "share" / app_name

    return data_dir
