from typing import Union
import numpy as np
from dataclasses import dataclass, field
from ..utils import create_uuid


@dataclass
class FrameData:
    frame_id: int
    frame: Union[np.ndarray, None]
    uuid: str = field(default_factory=lambda: create_uuid())


__all__ = [FrameData.__name__]
