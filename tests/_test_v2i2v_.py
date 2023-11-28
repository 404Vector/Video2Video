import asyncio
import os
from typing import List
import unittest

import numpy as np
from v2v import (
    Video2ImageProcessor,
    AudioExtractor,
    Image2VideoProcessor,
    AudioMerger,
    FrameData,
)
from . import _config_ as config


class TestVideo2Image2VideoProcessor(unittest.TestCase):
    def setUp(self) -> None:
        """
        모든 unittest 직전에 이 메서드가 호출됩니다.
        """

    def tearDown(self) -> None:
        """
        모든 unittest 직후에 이 메서드가 호출됩니다.
        """

    def test_v2i2v(self):
        v2ip = Video2ImageProcessor(
            video_path=config.test_v2i2v["test_video_url"],
            ffmpeg_options_output=config.test_v2i2v["v2i_ffmpeg_options_output"],
        )
        frames: List[FrameData] = []
        while True:
            frame = v2ip()
            frames.append(frame)
            if frame is None:
                break

        v2ap = AudioExtractor(
            video_path=config.test_v2i2v["test_video_url"],
            dst_audio_path=config.test_v2i2v["dst_audio_path"],
            ffmpeg_options_output=config.test_v2i2v["v2a_ffmpeg_options_output"],
        )
        v2ap.run()

        i2vp = Image2VideoProcessor(
            dst_video_path=config.test_v2i2v["dst_video_path"],
            width=v2ip.video_info.frame_width,
            height=v2ip.video_info.frame_height,
            fps=v2ip.video_info.avg_frame_rate,
            ffmpeg_options_input=config.test_v2i2v["i2v_ffmpeg_options_input"],
            ffmpeg_options_output=config.test_v2i2v["i2v_ffmpeg_options_output"],
        )
        try:
            while True:
                frame_data = frames.pop(0)
                if frame_data is not None:
                    image = frame_data.frame
                    image = np.clip(
                        (image.astype(np.int32) - 32) * (128.0 / (128 - 32)), 0, 255
                    )
                    frame_data.frame = image
                i2vp(frame_data=frame_data)
                if frame_data is None:
                    break
        except StopIteration:
            pass
        va2vp = AudioMerger(
            video_path=config.test_v2i2v["dst_video_path"],
            audio_path=config.test_v2i2v["dst_audio_path"],
            dst_video_path=config.test_v2i2v["dst_video_audio_path"],
        )
        va2vp.run()
        for path in [
            config.test_v2i2v["dst_video_path"],
            config.test_v2i2v["dst_audio_path"],
            config.test_v2i2v["dst_video_audio_path"],
        ]:
            self.assertEqual(os.path.exists(path), True)
            os.remove(path=path)
            self.assertEqual(os.path.exists(path), False)
