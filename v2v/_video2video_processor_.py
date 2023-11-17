import asyncio
from asyncio import Queue, Task
import functools
import os
from typing import Generator, Optional, Union
from v2v.datastruct import VideoInfo, FrameData
from v2v.utils import (
    create_uuid,
)

from v2v import (
    Video2ImageProcessor,
    Image2VideoProcessor,
    AudioExtractor,
    AudioMerger,
    IFrameProcessorPool,
    NullFrameProcessorPool,
)


def _create_video2image_task(v2i_proc: Video2ImageProcessor, queue: Queue) -> Task:
    async def __job(v2i_proc: Video2ImageProcessor, queue: Queue):
        while True:
            frame_data = await v2i_proc()
            await queue.put(frame_data)
            if frame_data.frame is None:
                break

    task = asyncio.create_task(__job(v2i_proc=v2i_proc, queue=queue))
    return task


def _create_video2audio_task(v2a_proc: AudioExtractor) -> Task:
    task = asyncio.create_task(asyncio.to_thread(v2a_proc.run))
    return task


def _create_image2video_task(i2v_proc: Image2VideoProcessor, queue: Queue) -> Task:
    async def __job(i2v_proc: Image2VideoProcessor, queue: Queue):
        while True:
            frame_data: FrameData = await queue.get()
            await i2v_proc(frame_data=frame_data)
            if frame_data.frame is None:
                break

    task = asyncio.create_task(__job(i2v_proc=i2v_proc, queue=queue))
    return task


def _create_videoaudio2video_task(va2v_proc: AudioMerger) -> Task:
    task = asyncio.create_task(asyncio.to_thread(va2v_proc.run))
    return task


def _create_i2i_processing_task(
    i2i_pool: IFrameProcessorPool,
    input_queue: Queue,
    output_queue: Queue,
) -> Task:
    async def __job(
        i2i_pool: IFrameProcessorPool,
        input_queue: Queue,
        output_queue: Queue,
    ):
        while True:
            frame_data: FrameData = await input_queue.get()
            if frame_data.frame is not None:
                frame_data = await i2i_pool(frame_data=frame_data)

            await output_queue.put(frame_data)
            if frame_data.frame is None:
                break

    task = asyncio.create_task(
        __job(
            i2i_pool=i2i_pool,
            input_queue=input_queue,
            output_queue=output_queue,
        )
    )
    return task


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
        i2v_queue = Queue(self.i2v_queue_size)
        video2image_task = _create_video2image_task(
            v2i_proc=video2image_proc,
            queue=v2i_queue,
        )
        video2audio_task = _create_video2audio_task(v2a_proc=video2audio_proc)
        image2image_task = _create_i2i_processing_task(
            i2i_pool=image2image_pool,
            input_queue=v2i_queue,
            output_queue=i2v_queue,
        )
        image2video_task = _create_image2video_task(
            i2v_proc=image2video_proc, queue=i2v_queue
        )
        await asyncio.gather(
            video2image_task,
            video2audio_task,
            image2image_task,
            image2video_task,
        )
        videoaudio2video_task = _create_videoaudio2video_task(
            va2v_proc=videoaudio2video_proc
        )
        await videoaudio2video_task
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
