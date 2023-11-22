from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar
from ..utils import create_uuid

IT = TypeVar("IT")
OT = TypeVar("OT")


class IFrameProcessor(Generic[IT, OT], metaclass=ABCMeta):
    def __init__(self) -> None:
        self._id = create_uuid()

    @abstractmethod
    async def __call__(self, input_data: IT) -> OT:
        ...

    @abstractmethod
    def _get_ready(self) -> bool:
        ...

    @abstractmethod
    def _get_live(self) -> bool:
        ...

    @property
    def id(self):
        assert self._id is not None
        return self._id

    @property
    def live(self) -> bool:
        __val = self._get_live()
        assert type(__val) is bool
        return __val

    @property
    def ready(self) -> bool:
        __val = self._get_ready()
        assert type(__val) is bool
        return __val


__all__ = [IFrameProcessor.__name__]
