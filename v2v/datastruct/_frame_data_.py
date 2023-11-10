import numpy as np
from dataclasses import dataclass, field
from v2v.utils import create_uuid


@dataclass
class FrameData:
    frame_id: int
    frame: np.ndarray
    uuid: str = field(default_factory=lambda: create_uuid())


__all__ = [FrameData.__name__]
