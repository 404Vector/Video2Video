from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar
from v2v.utils import create_uuid

IT = TypeVar("IT")
OT = TypeVar("OT")


class IFrameProcessor(Generic[IT, OT], metaclass=ABCMeta):
    def __init__(self) -> None:
        self._id = create_uuid()

    @abstractmethod
    async def __call__(self, input_data: IT) -> OT:
        ...

    @property
    def id(self):
        return self._id

    @property
    @abstractmethod
    def live(self) -> bool:
        ...

    @property
    @abstractmethod
    def ready(self) -> bool:
        ...


__all__ = [IFrameProcessor.__name__]
