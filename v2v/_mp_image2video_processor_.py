from typing import Optional
from . import Image2VideoProcessor
import multiprocessing as mp
import asyncio
import uvloop


def _create_i2v_processor(queue: mp.Queue, *args, **kwargs):
    # use uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    proc = Image2VideoProcessor(*args, **kwargs)

    async def __main(processor: Image2VideoProcessor, queue: mp.Queue):
        while True:
            frame_data = queue.get()
            await processor(frame_data=frame_data)
            if frame_data.frame is None:
                break

    asyncio.run(__main(processor=proc, queue=queue))


class MPImage2VideoProcessor:
    def __init__(self, mp_queue: mp.Queue, *args, **kwargs) -> None:
        self._processor = mp.Process(
            target=_create_i2v_processor, args=(mp_queue, *args), kwargs=kwargs
        )

    def run(self):
        self._processor.start()

    def join(self):
        self._processor.join()


__all__ = [
    MPImage2VideoProcessor.__name__,
]
