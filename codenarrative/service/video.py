import domain.rendering
import domain.storage
import subprocess

def render_video(location: domain.storage.Location, state: domain.rendering.SceneState):
    png_file_mask = location.file('%05d', "png")
    video_file = location.file("out", "mp4")
    subprocess.run(
        [
        "ffmpeg",
        "-framerate", str(state.profile.fps),
        "-i", png_file_mask,
        "-c:v", "libx264",
        "-vf", "fps=" + str(state.profile.fps),
        "-pix_fmt", "yuv420p",
        video_file
        ]
    )
