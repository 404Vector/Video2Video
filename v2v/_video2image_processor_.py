import asyncio
import functools
from typing import Any, Generator, Optional, Union
from .datastruct import FrameData, VideoInfo
from .utils import (
    read_frame_from_process,
    get_video_info_from_path,
    create_v2i_process,
    create_uuid,
)


class Video2ImageProcessor:
    def __init__(self, video_path: str, ffmpeg_options_output: Optional[dict] = None):
        self._id = create_uuid()
        self._video_path = video_path
        self._video_info = VideoInfo(get_video_info_from_path(video_path=video_path))
        self._ffmpeg_options_output = ffmpeg_options_output
        self._sub_processor = create_v2i_process(
            video_path=video_path,
            ffmpeg_options_output=ffmpeg_options_output,
        )
        assert self._sub_processor is not None
        self._progress = 0
        self._is_done = False

    def __call__(self) -> FrameData:
        assert self._is_done is False
        frame = read_frame_from_process(
            process=self._sub_processor,
            width=self._video_info.frame_width,
            height=self._video_info.frame_height,
        )

        if frame is not None:
            frame_data = FrameData(frame_id=self._progress, frame=frame)
            self._progress += 1
        else:
            self._is_done = True
            frame_data = None
            self._sub_processor.stdout.close()
            self._sub_processor.wait()
        return frame_data

    @property
    def id(self) -> str:
        return self._id

    @property
    def video_info(self) -> VideoInfo:
        return self._video_info

    @property
    def video_path(self) -> str:
        return self._video_path


__all__ = [Video2ImageProcessor.__name__]
