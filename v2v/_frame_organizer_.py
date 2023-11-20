from typing import Dict
from . import FrameData
import asyncio
from asyncio import Queue


class FrameOrganizer:
    def __init__(
        self,
        input_queue_size: int = 60,
        output_queue_size: int = 60,
        skip_delay: float = 0.1,
    ):
        assert skip_delay > 0
        assert input_queue_size > 0
        assert output_queue_size > 0

        self._flag_running_state = True

        async def _run_get_queue(
            organizer: FrameOrganizer,
            temp_storage: Dict[int, FrameData],
            input_queue: Queue,
            delay: float,
        ):
            while organizer.flag_state:
                if input_queue.empty():
                    await asyncio.sleep(delay=delay)
                    continue
                frame_data: FrameData = await input_queue.get()
                assert temp_storage.get(frame_data.frame_id) is None
                temp_storage[frame_data.frame_id] = frame_data

        async def _run_set_queue(
            organizer: FrameOrganizer,
            temp_storage: Dict[int, FrameData],
            output_queue: Queue,
            delay: float,
        ):
            target_id = 0
            while organizer.flag_state:
                if output_queue.full() or temp_storage.get(target_id) is None:
                    await asyncio.sleep(delay=delay)
                    continue
                frame_data: FrameData = temp_storage.pop(target_id)
                await output_queue.put(frame_data)
                target_id += 1

        temp_storage = {}
        self._input_queue = Queue(input_queue_size)
        self._output_queue = Queue(output_queue_size)
        self._skip_delay = skip_delay
        self._input_task = asyncio.create_task(
            _run_get_queue(
                organizer=self,
                temp_storage=temp_storage,
                input_queue=self._input_queue,
                delay=self._skip_delay,
            )
        )
        self._output_task = asyncio.create_task(
            _run_set_queue(
                organizer=self,
                temp_storage=temp_storage,
                output_queue=self._output_queue,
                delay=self._skip_delay,
            )
        )

    async def async_close(self):
        self._flag_running_state = False
        await asyncio.gather(
            self._input_task,
            self._output_task,
        )

    @property
    def flag_state(self) -> bool:
        return self._flag_running_state

    @property
    def input_queue(self) -> Queue[FrameData]:
        return self._input_queue

    @property
    def output_queue(self) -> Queue[FrameData]:
        return self._output_queue

    @property
    def delay(self) -> int:
        return self._skip_delay
