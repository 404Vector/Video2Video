import os
import unittest
from v2v import Image2VideoProcessor
from . import _config_ as config
import numpy as np
from v2v.datastruct import FrameData


class TestImage2VideoProcessor(unittest.TestCase):
    def setUp(self) -> None:
        """
        모든 unittest 직전에 이 메서드가 호출됩니다.
        """

    def tearDown(self) -> None:
        """
        모든 unittest 직후에 이 메서드가 호출됩니다.
        """

    def test_encode_frames(self):
        width = config.test_i2vp["test_video_width"]
        height = config.test_i2vp["test_video_height"]
        fps = config.test_i2vp["test_video_fps"]
        colors = config.test_i2vp["test_video_color_sequence"]
        frame_datas = [
            FrameData(fid, (np.ones((height, width, 3)) * c).astype(np.uint8))
            for fid, c in enumerate(colors)
        ]
        i2vp = Image2VideoProcessor(
            dst_video_path=config.test_i2vp["dst_video_path"],
            nb_frames=len(frame_datas),
            width=width,
            height=height,
            fps=fps,
            ffmpeg_options_input=config.test_i2vp["ffmpeg_options_input"],
            ffmpeg_options_output=config.test_i2vp["ffmpeg_options_output"],
        )
        image_stream = i2vp.create_stream()
        try:
            for fid, frame_data in enumerate(frame_datas):
                self.assertEqual(fid, frame_data.frame_id)
                image_stream.send(frame_data)
        except StopIteration:
            pass
        self.assertEqual(
            os.path.exists(i2vp.dst_video_path),
            True,
            f"{i2vp.dst_video_path} is not exist!",
        )
        os.remove(i2vp.dst_video_path)
        self.assertEqual(
            os.path.exists(i2vp.dst_video_path),
            False,
            f"{i2vp.dst_video_path} is not deleted!",
        )
