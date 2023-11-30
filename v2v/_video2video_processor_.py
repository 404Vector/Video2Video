import asyncio
from asyncio import Task
from queue import Queue
import functools
import os
from typing import Generator, Optional, Tuple, Union
import threading
import numpy as np
from .datastruct import VideoInfo, FrameData, ThreadSafeProgress
from .utils import (
    create_uuid,
    create_v2v_process,
    read_frame_from_process,
    get_video_info_from_path,
)
import subprocess

from . import (
    IFrameProcessorPool,
    NullFrameProcessorPool,
)


def job_video2image(
    v2i_proc: subprocess.Popen,
    video_info: VideoInfo,
    enqueue: Queue,
    progress: ThreadSafeProgress,
):
    frame_width = video_info.frame_width
    frame_height = video_info.frame_height
    while True:
        frame = read_frame_from_process(
            process=v2i_proc,
            width=frame_width,
            height=frame_height,
        )
        if frame is None:
            break
        frame_data = FrameData(frame_id=progress.progress, frame=frame)
        # print(f"v2i[{frame_data.frame_id:05d}]")
        enqueue.put(frame_data)
        progress.change(1)
    enqueue.put(None)  # end of work
    v2i_proc.stdout.close()
    v2i_proc.wait()


def job_image2image(
    i2i_pool: IFrameProcessorPool,
    dequeue: Queue,
    enqueue: Queue,
    progress: ThreadSafeProgress,
):
    loop = asyncio.new_event_loop()
    number_of_process = len(i2i_pool)

    async def _processing(
        i2i_pool: IFrameProcessorPool,
        dequeue: Queue,
        enqueue: Queue,
        progress: ThreadSafeProgress,
    ):
        while True:
            frame_data: FrameData = dequeue.get()
            if frame_data is None:
                dequeue.put(None)
                break
            result = await i2i_pool(frame_data=frame_data)
            # print(f"--------i2i[{frame_data.frame_id:05d}]")
            enqueue.put(result)
            progress.change(1)
        enqueue.put(None)  # end of work

    loop.run_until_complete(
        asyncio.gather(
            *[
                loop.create_task(
                    _processing(
                        i2i_pool=i2i_pool,
                        dequeue=dequeue,
                        enqueue=enqueue,
                        progress=progress,
                    )
                )
                for _ in range(number_of_process)
            ]
        )
    )


def job_image2video(
    i2v_proc: subprocess.Popen,
    i2i_pool: IFrameProcessorPool,
    dequeue: Queue,
    progress: ThreadSafeProgress,
):
    temp_state = {}
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
        while progress.progress in temp_state:
            target_item: FrameData = temp_state.pop(progress.progress)
            i2v_proc.stdin.write(target_item.frame.astype(np.uint8).tobytes())
            progress.change(1)
    # end of work
    i2v_proc.stdin.close()
    i2v_proc.wait()


class Video2VideoProcessor:
    def __init__(
        self,
        input_video_path: str,
        output_video_path: str,
        frame_processor_pool: IFrameProcessorPool = NullFrameProcessorPool(
            1, 0.0001, 0.01
        ),
        i2v_frame_size: Optional[Tuple[int, int]] = None,
        i2v_fps: Optional[Union[str, float, int]] = None,
        dst_ffmpeg_options_output: Optional[dict] = None,
    ) -> None:
        self._id = create_uuid()
        self._input_video_path = input_video_path
        self._output_video_path = output_video_path

        v2ip, i2vp = create_v2v_process(
            video_path=input_video_path,
            dst_video_path=output_video_path,
            dst_fps=i2v_fps,
            dst_frame_size=i2v_frame_size,
            dst_ffmpeg_options_output=dst_ffmpeg_options_output,
        )

        self._v2i_proc = v2ip
        self._i2v_proc = i2vp
        self._input_video_info = VideoInfo(
            get_video_info_from_path(video_path=input_video_path)
        )
        self._frame_processor_pool = frame_processor_pool
        self._is_running = False
        self._main_task: Optional[Task] = None
        self._v2i_progress = ThreadSafeProgress(
            "v2i", max_progress=self._input_video_info.nb_frames
        )
        self._i2i_progress = ThreadSafeProgress(
            "i2i", max_progress=self._input_video_info.nb_frames
        )
        self._i2v_progress = ThreadSafeProgress(
            "i2v", max_progress=self._input_video_info.nb_frames
        )

    async def _async_run(self):
        self._is_running = True
        video2image_proc = self._v2i_proc
        image2image_pool = self._frame_processor_pool
        image2video_proc = self._i2v_proc
        video_info = self._input_video_info
        v2i_queue = Queue(len(image2image_pool))
        i2v_queue = Queue(len(image2image_pool))
        v2i_progress = self._v2i_progress
        i2i_progress = self._i2i_progress
        i2v_progress = self._i2v_progress
        await asyncio.gather(
            asyncio.to_thread(
                job_video2image,
                v2i_proc=video2image_proc,
                video_info=video_info,
                enqueue=v2i_queue,
                progress=v2i_progress,
            ),
            asyncio.to_thread(
                job_image2image,
                i2i_pool=image2image_pool,
                dequeue=v2i_queue,
                enqueue=i2v_queue,
                progress=i2i_progress,
            ),
            asyncio.to_thread(
                job_image2video,
                i2v_proc=image2video_proc,
                i2i_pool=image2image_pool,
                dequeue=i2v_queue,
                progress=i2v_progress,
            ),
        )
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
    def is_running(self) -> bool:
        return self._is_running

    @property
    def input_video_info(self) -> VideoInfo:
        return self._input_video_info

    @property
    def v2i_progress(self) -> ThreadSafeProgress:
        return self._v2i_progress

    @property
    def i2i_progress(self) -> ThreadSafeProgress:
        return self._i2i_progress

    @property
    def i2v_progress(self) -> ThreadSafeProgress:
        return self._i2v_progress


__all__ = [Video2VideoProcessor.__name__]
