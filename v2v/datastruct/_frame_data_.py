import uuid
import numpy as np
from dataclasses import dataclass, field


@dataclass
class FrameData:
    frame_id: int
    frame: np.ndarray
    uuid: str = field(default_factory=lambda: str(uuid.uuid1()))


__all__ = [FrameData.__name__]
