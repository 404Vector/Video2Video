import asyncio
from typing import Optional
from .datastruct import VideoInfo
from .utils import (
    get_video_info_from_path,
    create_v2a_process,
    create_uuid,
)


class AudioExtractor:
    def __init__(
        self,
        video_path: str,
        dst_audio_path: str,
        ffmpeg_options_output: Optional[dict] = None,
    ):
        self._id = create_uuid()
        self._video_path = video_path
        self._dst_audio_path = dst_audio_path
        self._video_info = VideoInfo(get_video_info_from_path(video_path=video_path))
        self._ffmpeg_options_output = ffmpeg_options_output

    def run(self):
        video_info = self.video_info
        video_path = self.video_path
        dst_audio_path = self.dst_audio_path
        info = video_info
        ffmpeg_options_output = self._ffmpeg_options_output
        processor = create_v2a_process(
            video_path=video_path,
            dst_audio_path=dst_audio_path,
            ffmpeg_options_output=ffmpeg_options_output,
        )
        assert processor is not None
        processor.wait()

    @property
    def id(self) -> str:
        return self._id

    @property
    def video_info(self) -> VideoInfo:
        return self._video_info

    @property
    def video_path(self) -> str:
        return self._video_path

    @property
    def dst_audio_path(self) -> str:
        return self._dst_audio_path


__all__ = [AudioExtractor.__name__]
