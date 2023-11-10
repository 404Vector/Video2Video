import subprocess
from typing import Generator
from v2v.datastruct import FrameData, VideoInfo
from v2v.utils import (
    read_frame_from_process,
    get_video_info_from_path,
    create_vi2_process,
    create_uuid,
)


class Video2ImageProcessor:
    def __init__(self, video_path: str):
        self._id = create_uuid()
        self._video_path = video_path
        self._video_info = VideoInfo(get_video_info_from_path(video_path=video_path))

    @classmethod
    def __create_frame_generator(
        cls,
        video_path: str,
        video_info: VideoInfo,
    ) -> FrameData:
        info = video_info
        processor = create_vi2_process(video_path=video_path)
        assert processor is not None
        for _frame_id in range(info.nb_frames):
            frame = read_frame_from_process(
                process=processor,
                width=info.frame_width,
                height=info.frame_height,
            )
            yield FrameData(frame_id=_frame_id, frame=frame)
        processor.wait()

    def create_stream(self) -> Generator[FrameData, None, None]:
        return self.__create_frame_generator(
            video_info=self.video_info,
            video_path=self.video_path,
        )

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
