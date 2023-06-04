from codenarrative.domain.scene import Profile
from codenarrative.domain.storage import Location
import subprocess

from codenarrative.service import sound_service


def render_video(location: Location, profile: Profile):
    png_file_mask = location.file("%06d", "png")
    wav_file = location.file(sound_service.OUTPUT_WAV_FILENAME_NO_EXTENSION, "wav")
    video_file = location.file("out", "mp4")
    subprocess.run(
        [
            "ffmpeg",
            "-framerate",
            str(profile.fps),
            "-i",
            png_file_mask,
            "-i",
            wav_file,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-vf",
            "fps=" + str(profile.fps),
            "-pix_fmt",
            "yuv420p",
            video_file,
        ]
    )
