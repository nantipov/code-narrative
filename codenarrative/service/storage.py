import domain.storage
import time
import pathlib

def location() -> domain.storage.Location:
    loc = domain.storage.Location()
    directory_name = round(time.time() * 1000)
    loc.directory_name = f"output/{directory_name}"
    pathlib.Path(loc.directory_name).mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/html").mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/png").mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/css").mkdir(parents=True, exist_ok=True)
    pathlib.Path(loc.directory_name + "/mp4").mkdir(parents=True, exist_ok=True)
    return loc

