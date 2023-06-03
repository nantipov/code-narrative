class Location:
    directory_name: str

    def frame_file(self, frame: int, extension: str) -> str:
        (directory, file) = self.directory_and_frame_file(frame, extension)
        return f"{directory}/{file}"

    def directory_and_frame_file(self, frame: int, extension: str) -> tuple[str, str]:
        name = f"{frame:06}"
        return self.directory_and_file(name, extension)

    def file(self, name: str, extension: str) -> str:
        (directory, file) = self.directory_and_file(name, extension)
        return f"{directory}/{file}"

    def directory_and_file(self, name: str, extension: str) -> tuple[str, str]:
        return f"{self.directory_name}/{extension}", f"{name}.{extension}"
