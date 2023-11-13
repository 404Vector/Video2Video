from typing import Generator, Literal, Optional, Union

import numpy as np
from v2v.datastruct import FrameData
from v2v.utils import (
    create_i2v_process,
    create_uuid,
)


class Image2VideoProcessor:
    def __init__(
        self,
        dst_video_path: str,
        nb_frames: int,
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
        self._nb_frames = nb_frames

    @classmethod
    def __create_video_generator(
        cls,
        dst_video_path: str,
        nb_frames: int,
        width: int,
        height: int,
        fps: Union[str, float, int],
        ffmpeg_options_input: Optional[dict] = None,
        ffmpeg_options_output: Optional[dict] = None,
    ) -> FrameData:
        processor = create_i2v_process(
            dst_video_path=dst_video_path,
            width=width,
            height=height,
            fps=fps,
            ffmpeg_options_input=ffmpeg_options_input,
            ffmpeg_options_output=ffmpeg_options_output,
        )
        assert processor is not None
        for _frame_id in range(nb_frames):
            frame_data: FrameData = yield
            assert _frame_id == frame_data.frame_id
            if frame_data is None:
                break
            processor.stdin.write(frame_data.frame.astype(np.uint8).tobytes())
        processor.stdin.close()
        processor.wait()
        # yield True
        return True

    def create_stream(self) -> Generator[None, FrameData, None]:
        s = self.__create_video_generator(
            dst_video_path=self.dst_video_path,
            nb_frames=self._nb_frames,
            width=self._width,
            height=self._height,
            fps=self._fps,
            ffmpeg_options_input=self._ffmpeg_options_input,
            ffmpeg_options_output=self._ffmpeg_options_output,
        )
        s.send(None)
        return s

    @property
    def id(self) -> str:
        return self._id

    @property
    def dst_video_path(self) -> str:
        return self._dst_video_path


__all__ = [Image2VideoProcessor.__name__]
