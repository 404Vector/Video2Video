import asyncio
from typing import Generic, List, TypeVar
from .interface import IFrameProcessorPool
from . import FrameData, NullFrameProcessor


IT = TypeVar("IT")
OT = TypeVar("OT")


class NullFrameProcessorPool(IFrameProcessorPool):
    def __init__(
        self,
        number_of_processor: int = 1,
        processor_delay: float = 0.1,
        search_delay: float = 0.1,
    ) -> None:
        assert number_of_processor > 0
        assert processor_delay > 0
        assert search_delay > 0
        processors: List[NullFrameProcessor] = [
            NullFrameProcessor(delay=processor_delay)
            for _ in range(number_of_processor)
        ]
        super().__init__(processors, search_delay)

    async def __run__(
        self,
        target_processor: NullFrameProcessor,
        frame_data: FrameData,
    ) -> FrameData:
        return await target_processor(input_data=frame_data)


__all__ = [NullFrameProcessorPool.__name__]
