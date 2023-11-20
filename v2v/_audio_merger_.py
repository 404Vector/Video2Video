from typing import Optional
from .utils import (
    create_va2v_process,
    create_uuid,
)


class AudioMerger:
    def __init__(
        self,
        video_path: str,
        audio_path: str,
        dst_video_path: str,
        ffmpeg_options_output: Optional[dict] = None,
    ):
        self._id = create_uuid()
        self._video_path = video_path
        self._audio_path = audio_path
        self._dst_video_path = dst_video_path
        self._ffmpeg_options_output = ffmpeg_options_output

    def run(self):
        video_path = self.video_path
        audio_path = self.audio_path
        dst_video_path = self.dst_video_path
        ffmpeg_options_output = self._ffmpeg_options_output
        processor = create_va2v_process(
            video_path=video_path,
            audio_path=audio_path,
            dst_video_path=dst_video_path,
            ffmpeg_options_output=ffmpeg_options_output,
        )
        assert processor is not None
        processor.wait()

    @property
    def id(self) -> str:
        return self._id

    @property
    def video_path(self) -> str:
        return self._video_path

    @property
    def audio_path(self) -> str:
        return self._audio_path

    @property
    def dst_video_path(self) -> str:
        return self._dst_video_path


__all__ = [AudioMerger.__name__]
