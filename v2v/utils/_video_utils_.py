import subprocess
from typing import Any, Dict, Literal, Union
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


def get_video_info_from_path(video_path: str) -> dict:
    probe = ffmpeg.probe(video_path)
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    return video_info


def create_vi2_process(video_path: str) -> subprocess.Popen:
    output_kwargs: Dict[str, str] = {
        "format": "rawvideo",
        "pix_fmt": "rgb24",
    }
    args = ffmpeg.input(video_path).output("pipe:", **output_kwargs).compile()
    return subprocess.Popen(args, stdout=subprocess.PIPE)


def create_i2v_process(
    width: int,
    height: int,
    fps: Union[str, float, int],
    pix_fmt: str,
    video_bitrate: int,
    format: Literal["h264", "h265"],
) -> subprocess.Popen:
    input_kwargs: Dict[str, str] = {
        "format": "rawvideo",
        "pix_fmt": "rgb24",
        "s": f"{width}x{height}",
        "framerate": str(fps),
    }
    output_kwargs: Dict[str, str] = {
        "format": format,
        "pix_fmt": pix_fmt,
        "video_bitrate": video_bitrate,
    }
    pargs = (
        ffmpeg.input("pipe:", **input_kwargs)
        .output("pipe:", **output_kwargs)
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(pargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE)


__all__ = [
    read_frame_from_process.__name__,
    get_video_info_from_path.__name__,
    create_vi2_process.__name__,
]
