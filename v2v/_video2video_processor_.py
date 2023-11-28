import asyncio
from asyncio import Task
from queue import Queue
import functools
import os
from typing import Generator, Optional, Union
from .datastruct import VideoInfo, FrameData
from .utils import (
    create_uuid,
)

from . import (
    Video2ImageProcessor,
    Image2VideoProcessor,
    AudioExtractor,
    AudioMerger,
    IFrameProcessorPool,
    NullFrameProcessorPool,
)


def job_video2image(v2i_proc: Video2ImageProcessor, enqueue: Queue):
    while True:
        frame_data = v2i_proc()
        if frame_data is None:
            break
        enqueue.put(frame_data)
    enqueue.put(None)  # end of work


def job_video2audio(v2a_proc: AudioExtractor):
    v2a_proc.run()


async def job_image2image(
    i2i_pool: IFrameProcessorPool,
    dequeue: Queue,
    enqueue: Queue,
):
    while True:
        frame_data: FrameData = dequeue.get()
        if frame_data is None:
            dequeue.put(None)
            break
        result = await i2i_pool(frame_data=frame_data)
        enqueue.put(result)
    enqueue.put(None)  # end of work


def job_image2video(
    i2v_proc: Image2VideoProcessor,
    i2i_pool: IFrameProcessorPool,
    dequeue: Queue,
):
    temp_state = {}
    progress = 0
    n_worker = len(i2i_pool)
    while True:
        frame_data: FrameData = dequeue.get()
        if frame_data == None:
            n_worker -= 1
            if n_worker == 0:
                break
            else:
                continue
        key = frame_data.frame_id
        temp_state[key] = frame_data
        while progress in temp_state:
            target_item = temp_state.pop(progress)
            i2v_proc(frame_data=target_item)
            progress += 1
    i2v_proc(None)  # end of work


def job_merge_video_and_audio(va2v_proc: AudioMerger):
    va2v_proc.run()


class Video2VideoProcessor:
    def __init__(
        self,
        input_video_path: str,
        temp_file_dir: str,
        output_video_path: str,
        v2i_queue_size: int = 60,
        i2v_queue_size: int = 60,
        frame_processor_pool: IFrameProcessorPool = NullFrameProcessorPool(
            1, 0.0001, 0.01
        ),
        v2i_ffmpeg_options_output: Optional[dict] = None,
        v2a_ffmpeg_options_output: Optional[dict] = None,
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
        self._v2i_queue_size = v2i_queue_size
        self._i2v_queue_size = i2v_queue_size

        self._v2ip = Video2ImageProcessor(
            video_path=input_video_path,
            ffmpeg_options_output=v2i_ffmpeg_options_output,
        )
        i2v_width = i2v_width if i2v_width else self._v2ip.video_info.frame_width
        i2v_height = i2v_height if i2v_height else self._v2ip.video_info.frame_height
        i2v_fps = i2v_fps if i2v_fps else self._v2ip.video_info.avg_frame_rate
        i2v_ffmpeg_options_input = i2v_ffmpeg_options_input
        i2v_ffmpeg_options_output = i2v_ffmpeg_options_output

        self._i2vp = Image2VideoProcessor(
            dst_video_path=self.temp_video_path,
            width=i2v_width,
            height=i2v_height,
            fps=i2v_fps,
            ffmpeg_options_input=i2v_ffmpeg_options_input,
            ffmpeg_options_output=i2v_ffmpeg_options_output,
        )
        self._v2ap = AudioExtractor(
            video_path=self.input_video_path,
            dst_audio_path=self.temp_audio_path,
            ffmpeg_options_output=v2a_ffmpeg_options_output,
        )
        self._va2vp = AudioMerger(
            video_path=self.temp_video_path,
            audio_path=self.temp_audio_path,
            dst_video_path=self.output_video_path,
            ffmpeg_options_output=va2v_ffmpeg_options_output,
        )
        self._frame_processor_pool = frame_processor_pool
        self._is_running = False
        self._main_task: Optional[Task] = None

    async def _async_run(self):
        self._is_running = True
        video2image_proc = self._v2ip
        video2audio_proc = self._v2ap
        image2video_proc = self._i2vp
        image2image_pool = self._frame_processor_pool
        videoaudio2video_proc = self._va2vp
        v2i_queue = Queue(self.v2i_queue_size)
        i2i_queue = Queue(len(image2image_pool))
        await asyncio.gather(
            asyncio.to_thread(
                job_video2image,
                v2i_proc=video2image_proc,
                enqueue=v2i_queue,
            ),
            *[
                job_image2image(
                    i2i_pool=image2image_pool,
                    dequeue=v2i_queue,
                    enqueue=i2i_queue,
                )
                for _ in range(len(image2image_pool))
            ],
            asyncio.to_thread(
                job_image2video,
                i2v_proc=image2video_proc,
                i2i_pool=image2image_pool,
                dequeue=i2i_queue,
            ),
            asyncio.to_thread(
                job_video2audio,
                v2a_proc=video2audio_proc,
            ),
        )

        await asyncio.to_thread(
            job_merge_video_and_audio,
            va2v_proc=videoaudio2video_proc,
        )

        os.remove(video2audio_proc.dst_audio_path)
        os.remove(image2video_proc.dst_video_path)
        assert not os.path.exists(video2audio_proc.dst_audio_path)
        assert not os.path.exists(image2video_proc.dst_video_path)
        self._is_running = False

    async def async_run(self):
        if self._is_running:
            raise RuntimeError(
                f"This {Video2VideoProcessor.__name__} instance is already running."
            )
        await self._async_run()

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
    def i2v_processor(self) -> Image2VideoProcessor:
        return self._v2ip

    @property
    def temp_file_dir(self) -> str:
        return self._temp_file_dir

    @property
    def v2i_queue_size(self) -> str:
        return self._v2i_queue_size

    @property
    def i2v_queue_size(self) -> str:
        return self._i2v_queue_size

    @property
    def temp_video_path(self) -> str:
        return os.path.join(
            self.temp_file_dir, f"{self.id}.{self._output_video_path.split('.')[-1]}"
        )

    @property
    def temp_audio_path(self) -> str:
        return os.path.join(self.temp_file_dir, f"{self.id}.m4a")

    @property
    def is_running(self) -> bool:
        return self._is_running


__all__ = [Video2VideoProcessor.__name__]
