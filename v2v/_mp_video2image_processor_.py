from typing import Optional
from . import Video2ImageProcessor
import multiprocessing as mp
import asyncio
import uvloop


def _create_v2i_processor(queue: mp.Queue, *args, **kwargs):
    # use uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    proc = Video2ImageProcessor(*args, **kwargs)

    async def __main(processor: Video2ImageProcessor, queue: mp.Queue):
        while True:
            frame_data = await processor()
            queue.put(frame_data)
            print(f"put:{frame_data.frame_id}")
            if frame_data.frame is None:
                break

    asyncio.run(__main(processor=proc, queue=queue))


class MPVideo2ImageProcessor:
    def __init__(self, mp_queue: mp.Queue, *args, **kwargs) -> None:
        self._processor = mp.Process(
            target=_create_v2i_processor, args=(mp_queue, *args), kwargs=kwargs
        )

    def run(self):
        self._processor.start()

    def join(self):
        self._processor.join()


__all__ = [
    MPVideo2ImageProcessor.__name__,
]
