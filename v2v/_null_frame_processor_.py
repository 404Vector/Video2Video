import asyncio
from .interface import IFrameProcessor
from .datastruct import FrameData


class NullFrameProcessor(IFrameProcessor[FrameData, FrameData]):
    def __init__(self, delay: float) -> None:
        self._delay = delay
        self._ready = True

    async def __call__(self, input_data: FrameData) -> FrameData:
        self._ready = False
        await asyncio.sleep(delay=self._delay)
        output_data = input_data
        self._ready = True
        return output_data

    def _get_live(self) -> bool:
        return True

    def _get_ready(self) -> bool:
        return self._ready


__all__ = [NullFrameProcessor.__name__]
