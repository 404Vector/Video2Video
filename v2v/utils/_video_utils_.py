import subprocess
from typing import Any
import numpy as np
import ffmpeg


def read_frame_from_process(process: Any, width: int, height: int, channel: int = 3):
    # Note: RGB24 == 3 bytes per pixel.
    frame_size = width * height * channel
    in_bytes = process.stdout.read(frame_size)
    if len(in_bytes) == 0:
        frame = None
    else:
        assert len(in_bytes) == frame_size
        frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, channel])
    return frame


def get_video_info_from_path(video_path: str):
    probe = ffmpeg.probe(video_path)
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    return video_info


def create_vi2_process(video_path: str):
    args = (
        ffmpeg.input(video_path)
        .output("pipe:", format="rawvideo", pix_fmt="rgb24")
        .compile()
    )
    return subprocess.Popen(args, stdout=subprocess.PIPE)


__all__ = [
    read_frame_from_process.__name__,
    get_video_info_from_path.__name__,
    create_vi2_process.__name__,
]
