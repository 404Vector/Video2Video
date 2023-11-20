from abc import ABCMeta, abstractmethod
import asyncio
from typing import Generic, List, TypeVar
from ..utils import create_uuid
from ..datastruct import FrameData
from ._i_frame_processor_ import IFrameProcessor

IT = TypeVar("IT")
OT = TypeVar("OT")


async def search_ready(
    processors: List[IFrameProcessor[IT, OT]], delay: float
) -> IFrameProcessor[IT, OT]:
    readyed_processors: List[IFrameProcessor[IT, OT]] = []
    while True:
        readyed_processors = list(filter(lambda x: x.ready, processors))
        if len(readyed_processors) != 0:
            break
        await asyncio.sleep(delay=delay)
    return readyed_processors[0]


class IFrameProcessorPool(Generic[IT, OT], metaclass=ABCMeta):
    def __init__(
        self,
        processors: List[IFrameProcessor[IT, OT]],
        search_delay: float = 0.1,
    ) -> None:
        assert len(processors) > 0
        self._id = create_uuid()
        self._processors = processors
        self._search_delay = search_delay

    def __len__(self):
        return len(self._processors)

    @abstractmethod
    async def __run__(
        self,
        target_processor: IFrameProcessor[IT, OT],
        frame_data: FrameData,
    ) -> FrameData:
        ...

    async def run(
        self,
        frame_data: FrameData,
    ) -> FrameData:
        processors = self._processors

        target_processor = await search_ready(processors, delay=self.search_delay)
        output_data = await self.__run__(
            target_processor=target_processor,
            frame_data=frame_data,
        )
        return output_data

    async def __call__(
        self,
        frame_data: FrameData,
    ) -> FrameData:
        return await self.run(frame_data=frame_data)

    @property
    def id(self):
        return self._id

    @property
    def search_delay(self) -> float:
        return self._search_delay

    @search_delay.setter
    def search_delay(self, value: float):
        assert value > 0
        self._search_delay = value
