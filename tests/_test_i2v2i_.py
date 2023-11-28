import asyncio
import os
import unittest
from v2v import Image2VideoProcessor, Video2ImageProcessor
from . import _config_ as config
import numpy as np
from v2v.datastruct import FrameData


class TestI2V2I(unittest.TestCase):
    def setUp(self) -> None:
        """
        모든 unittest 직전에 이 메서드가 호출됩니다.
        """

    def tearDown(self) -> None:
        """
        모든 unittest 직후에 이 메서드가 호출됩니다.
        """

    def test_i2v2i(self):
        width = config.test_i2v2i["test_video_width"]
        height = config.test_i2v2i["test_video_height"]
        fps = config.test_i2v2i["test_video_fps"]
        colors = config.test_i2v2i["test_video_color_sequence"]
        input_frame_datas = [
            FrameData(fid, (np.ones((height, width, 3)) * c).astype(np.uint8))
            for fid, c in enumerate(colors)
        ]
        input_frame_datas.append(None)  # end of the frame
        i2vp = Image2VideoProcessor(
            dst_video_path=config.test_i2v2i["dst_video_path"],
            width=width,
            height=height,
            fps=fps,
            ffmpeg_options_input=config.test_i2v2i["ffmpeg_options_input"],
            ffmpeg_options_output=config.test_i2v2i["ffmpeg_options_output"],
        )

        frame_datas = input_frame_datas.copy()
        while True:
            frame_data = frame_datas.pop(0)
            i2vp(frame_data)
            if frame_data is None:
                break
        v2ip = Video2ImageProcessor(config.test_i2v2i["dst_video_path"])
        while True:
            output_frame_data = v2ip()
            if output_frame_data is None:
                break
            input_frame_data = input_frame_datas[output_frame_data.frame_id]
            self.assertEqual(input_frame_data.frame_id, output_frame_data.frame_id)
            input_avg_color = input_frame_data.frame.mean(axis=0).mean(axis=0)
            output_avg_color = output_frame_data.frame.mean(axis=0).mean(axis=0)
            davg_color = np.abs(input_avg_color - output_avg_color)
            self.assertLess(davg_color.mean(), 1)
        os.remove(i2vp.dst_video_path)
        self.assertEqual(
            os.path.exists(i2vp.dst_video_path),
            False,
            f"{i2vp.dst_video_path} is not deleted!",
        )
        return
