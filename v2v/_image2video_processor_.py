import asyncio
import functools
from typing import Any, Generator, Literal, Optional, Union

import numpy as np
from .datastruct import FrameData
from .utils import (
    create_i2v_process,
    create_uuid,
)


class Image2VideoProcessor:
    def __init__(
        self,
        dst_video_path: str,
        width: int,
        height: int,
        fps: Union[str, float, int],
        ffmpeg_options_input: Optional[dict] = None,
        ffmpeg_options_output: Optional[dict] = None,
    ):
        self._id = create_uuid()
        self._dst_video_path = dst_video_path
        self._width = width
        self._height = height
        self._fps = fps
        self._ffmpeg_options_input = ffmpeg_options_input
        self._ffmpeg_options_output = ffmpeg_options_output
        self._sub_processor = create_i2v_process(
            dst_video_path=dst_video_path,
            width=width,
            height=height,
            fps=fps,
            ffmpeg_options_input=ffmpeg_options_input,
            ffmpeg_options_output=ffmpeg_options_output,
        )
        assert self._sub_processor is not None
        self._progress = 0
        self._is_done = False

    def __call__(self, frame_data: FrameData):
        assert self._is_done is False
        if frame_data is not None:
            assert self._progress == frame_data.frame_id
            self._sub_processor.stdin.write(frame_data.frame.astype(np.uint8).tobytes())
            self._progress += 1
        else:
            self._is_done = True
            self._sub_processor.stdin.close()
            self._sub_processor.wait()

    @property
    def id(self) -> str:
        return self._id

    @property
    def dst_video_path(self) -> str:
        return self._dst_video_path


__all__ = [Image2VideoProcessor.__name__]
