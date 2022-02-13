import pathlib
import sys


def get_resource_path(relative_path: str) -> str:
    """
    Returns the relative path expression compatible with PyInstaller.

    Parameters
    ----------
    relative_path : str
        Relative path to convert.

    Returns
    -------
    str
        Relative path expression compatible with PyInstaller.
    """
    rel_path = pathlib.Path(relative_path)
    dev_base_path = pathlib.Path(__file__).resolve().parent
    base_path = getattr(sys, "_MEIPASS", dev_base_path)
    return base_path / rel_path
