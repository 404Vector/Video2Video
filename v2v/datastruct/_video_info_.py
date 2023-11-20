from dataclasses import dataclass, field
from ..utils import create_uuid


@dataclass
class VideoInfo:
    video_info: dict
    uuid: str = field(default_factory=lambda: create_uuid())

    @property
    def frame_width(self):
        return int(self.video_info["width"])

    @property
    def frame_height(self):
        return int(self.video_info["height"])

    @property
    def pix_fmt(self):
        return int(self.video_info["pix_fmt"])

    @property
    def codec_name(self):
        return int(self.video_info["codec_name"])

    @property
    def codec_long_name(self):
        return int(self.video_info["codec_long_name"])

    @property
    def avg_frame_rate(self):
        fps_str: str = self.video_info["avg_frame_rate"]

        return (
            float(fps_str.split("/")[0]) / float(fps_str.split("/")[1])
            if "/" in fps_str
            else float(fps_str)
        )

    @property
    def bit_rate(self):
        return int(self.video_info["bit_rate"])

    @property
    def nb_frames(self):
        return int(self.video_info["nb_frames"])

    @property
    def video_path(self):
        return self.video_info


__all__ = [VideoInfo.__name__]
