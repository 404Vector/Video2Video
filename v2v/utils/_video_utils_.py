import subprocess
from typing import Any, Dict, Literal, Optional, Union
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


def create_v2i_process(
    video_path: str,
    ffmpeg_options_output: Optional[dict] = None,
    ffmpeg_log_level: str = "warning",
) -> subprocess.Popen:
    output_kwargs: Dict[str, str] = {
        "format": "rawvideo",
        "pix_fmt": "rgb24",
    }
    if ffmpeg_options_output is not None:
        output_kwargs.update(ffmpeg_options_output)
    args = (
        ffmpeg.input(video_path)
        .output(
            "pipe:",
            loglevel=ffmpeg_log_level,
            **output_kwargs,
        )
        .compile()
    )
    return subprocess.Popen(args, stdout=subprocess.PIPE)


def create_v2a_process(
    video_path: str,
    dst_audio_path: str,
    ffmpeg_options_output: Optional[dict] = None,
    ffmpeg_log_level: str = "warning",
) -> subprocess.Popen:
    output_kwargs: Dict[str, str] = {
        "vn": None,
        "c:a": "copy",
    }
    if ffmpeg_options_output is not None:
        output_kwargs.update(ffmpeg_options_output)
    args = (
        ffmpeg.input(video_path)
        .output(
            dst_audio_path,
            loglevel=ffmpeg_log_level,
            **output_kwargs,
        )
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(args)


def create_va2v_process(
    video_path: str,
    audio_path: str,
    dst_video_path: str,
    ffmpeg_options_output: Optional[dict] = None,
    ffmpeg_log_level: str = "warning",
) -> subprocess.Popen:
    output_kwargs: Dict[str, str] = {}
    if ffmpeg_options_output is not None:
        output_kwargs.update(ffmpeg_options_output)
    args = (
        ffmpeg.concat(
            ffmpeg.input(video_path),
            ffmpeg.input(audio_path),
            v=1,
            a=1,
        )
        .output(
            dst_video_path,
            loglevel=ffmpeg_log_level,
            **output_kwargs,
        )
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(args)


def create_i2v_process(
    dst_video_path: str,
    width: int,
    height: int,
    fps: Union[str, float, int],
    ffmpeg_options_input: Optional[dict] = None,
    ffmpeg_options_output: Optional[dict] = None,
    ffmpeg_log_level: str = "warning",
) -> subprocess.Popen:
    input_kwargs: Dict[str, str] = {
        "format": "rawvideo",
        "pix_fmt": "rgb24",
        "s": f"{width}x{height}",
        "framerate": str(fps),
    }
    output_kwargs: Dict[str, str] = {}
    if ffmpeg_options_input is not None:
        input_kwargs.update(ffmpeg_options_input)
    if ffmpeg_options_output is not None:
        output_kwargs.update(ffmpeg_options_output)
    pargs = (
        ffmpeg.input(
            "pipe:",
            **input_kwargs,
        )
        .output(
            dst_video_path,
            loglevel=ffmpeg_log_level,
            **output_kwargs,
        )
        .overwrite_output()
        .compile()
    )
    return subprocess.Popen(pargs, stdin=subprocess.PIPE)


__all__ = [
    read_frame_from_process.__name__,
    get_video_info_from_path.__name__,
    create_v2i_process.__name__,
    create_v2a_process.__name__,
    create_i2v_process.__name__,
    create_va2v_process.__name__,
]
