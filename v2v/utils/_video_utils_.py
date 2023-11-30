import subprocess
from typing import Any, Dict, Literal, Optional, Tuple, Union
import numpy as np
import ffmpeg


def read_frame_from_process(
    process: subprocess.Popen, width: int, height: int, channel: int = 3
):
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


def create_v2v_process(
    video_path: str,
    dst_video_path: str,
    ffmpeg_log_level: str = "warning",
    dst_frame_size: Optional[Tuple[int, int]] = None,
    dst_fps: Optional[Union[str, float, int]] = None,
    dst_ffmpeg_options_output: Optional[dict] = None,
) -> subprocess.Popen:
    output_kwargs: Dict[str, str] = {}
    if dst_ffmpeg_options_output is not None:
        output_kwargs.update(dst_ffmpeg_options_output)
    video_info = get_video_info_from_path(video_path=video_path)
    org_frame_width = video_info["width"]
    org_frame_height = video_info["height"]
    org_fps = video_info["avg_frame_rate"]
    dst_width = org_frame_width if dst_frame_size is None else dst_frame_size[0]
    dst_height = org_frame_height if dst_frame_size is None else dst_frame_size[1]
    dst_fps = org_fps if dst_fps is None else dst_fps
    video_stream = ffmpeg.input(video_path).video
    audio_stream = ffmpeg.input(video_path).audio

    # extract frame from video
    input_process_args = video_stream.output(
        "pipe:", format="rawvideo", pix_fmt="rgb24", loglevel=ffmpeg_log_level
    ).compile()
    input_process = subprocess.Popen(input_process_args, stdout=subprocess.PIPE)

    # merge frame and audio stream into video
    i2v_stream = ffmpeg.input(
        "pipe:",
        format="rawvideo",
        pix_fmt="rgb24",
        s="{}x{}".format(dst_width, dst_height),
        r=dst_fps,
    )
    output_process_args = (
        ffmpeg.concat(i2v_stream, audio_stream, v=1, a=1)
        .output(
            dst_video_path,
            pix_fmt="yuv420p",
            loglevel=ffmpeg_log_level,
            **output_kwargs,
        )
        .overwrite_output()
        .compile()
    )
    output_process = subprocess.Popen(output_process_args, stdin=subprocess.PIPE)
    return input_process, output_process


__all__ = [
    read_frame_from_process.__name__,
    get_video_info_from_path.__name__,
    create_v2i_process.__name__,
    create_v2a_process.__name__,
    create_i2v_process.__name__,
    create_va2v_process.__name__,
    create_v2v_process.__name__,
]
