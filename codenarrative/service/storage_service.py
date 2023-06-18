import os.path

import codenarrative
from codenarrative.domain.storage import Location
import time
import pathlib


def location() -> Location:
    loc = Location()
    directory_name = round(time.time() * 1000)
    loc.directory_name = f"output/{directory_name}"
    pathlib.Path(loc.directory_name).mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/png").mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/mp4").mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/wav").mkdir(parents=True, exist_ok=True)
    return loc


def app_file(filename: str) -> str:
    paths = codenarrative.__path__
    for app_path in paths:
        filepath = f"{app_path}/../{filename}"
        if os.path.exists(filepath):
            return filepath
    return filename
