from codenarrative.domain.scene import Profile
from codenarrative.domain.storage import Location
import subprocess


def render_video(location: Location, profile: Profile):
    png_file_mask = location.file("%06d", "png")
    video_file = location.file("out", "mp4")
    subprocess.run(
        [
            "ffmpeg",
            "-framerate",
            str(profile.fps),
            "-i",
            png_file_mask,
            "-c:v",
            "libx264",
            "-vf",
            "fps=" + str(profile.fps),
            "-pix_fmt",
            "yuv420p",
            video_file,
        ]
    )
