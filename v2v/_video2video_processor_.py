import asyncio
import os
from typing import Optional, Union
from v2v.datastruct import VideoInfo
from v2v.utils import (
    create_uuid,
)

from v2v import Video2ImageProcessor, Image2VideoProcessor, AudioExtractor, AudioMerger


class Video2VideoProcessor:
    def __init__(
        self,
        input_video_path: str,
        temp_file_dir: str,
        output_video_path: str,
        v2i_queue_size: int = 60,
        i2v_queue_size: int = 60,
        v2i_ffmpeg_options_output: Optional[dict] = None,
        v2a_ffmpeg_options_output: Optional[dict] = None,
        i2v_nb_frames: Optional[int] = None,
        i2v_width: Optional[int] = None,
        i2v_height: Optional[int] = None,
        i2v_fps: Optional[Union[str, float, int]] = None,
        i2v_ffmpeg_options_input: Optional[dict] = None,
        i2v_ffmpeg_options_output: Optional[dict] = None,
        va2v_ffmpeg_options_output: Optional[dict] = None,
    ) -> None:
        assert os.path.isdir(temp_file_dir)
        self._id = create_uuid()
        self._input_video_path = input_video_path
        self._temp_file_dir = temp_file_dir
        self._output_video_path = output_video_path

        self._v2ip = Video2ImageProcessor(
            video_path=input_video_path,
            ffmpeg_options_output=v2i_ffmpeg_options_output,
        )
        i2v_nb_frames = (
            i2v_nb_frames if i2v_nb_frames else self.i2v_processor.video_info.nb_frames
        )
        i2v_width = (
            i2v_width if i2v_width else self.i2v_processor.video_info.frame_width
        )
        i2v_height = (
            i2v_height if i2v_height else self.i2v_processor.video_info.frame_height
        )
        i2v_fps = i2v_fps if i2v_fps else self.i2v_processor.video_info.avg_frame_rate
        i2v_ffmpeg_options_input = i2v_ffmpeg_options_input
        i2v_ffmpeg_options_output = i2v_ffmpeg_options_output

        self._i2vp = Image2VideoProcessor(
            dst_video_path=self.temp_video_path,
            nb_frames=i2v_nb_frames,
            width=i2v_width,
            height=i2v_height,
            fps=i2v_fps,
            ffmpeg_options_input=i2v_ffmpeg_options_input,
            ffmpeg_options_output=i2v_ffmpeg_options_output,
        )
        self._v2ap = AudioExtractor(
            video_path=self.temp_video_path,
            dst_audio_path=self.temp_audio_path,
            ffmpeg_options_output=v2a_ffmpeg_options_output,
        )
        self._va2vp = AudioMerger(
            video_path=self.temp_video_path,
            audio_path=self.temp_audio_path,
            dst_video_path=self.output_video_path,
            ffmpeg_options_output=va2v_ffmpeg_options_output,
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def input_video_path(self) -> str:
        return self._input_video_path

    @property
    def output_video_path(self) -> str:
        return self._output_video_path

    @property
    def i2v_processor(self):
        return self._v2ip

    @property
    def temp_file_dir(self):
        return self._temp_file_dir

    @property
    def temp_video_path(self):
        return os.path.join(
            self.temp_file_dir, f"{self.id}.{self.input_video_path.split('.')[-1]}"
        )

    @property
    def temp_audio_path(self):
        return os.path.join(self.temp_file_dir, f"{self.id}.m4a")


__all__ = [Video2ImageProcessor.__name__]
