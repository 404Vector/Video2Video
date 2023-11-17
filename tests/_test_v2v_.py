import asyncio
import os
import unittest

import numpy as np
from v2v import Video2VideoProcessor
from . import _config_ as config


class TestVideo2VideoProcessor(unittest.TestCase):
    def setUp(self) -> None:
        """
        모든 unittest 직전에 이 메서드가 호출됩니다.
        """

    def tearDown(self) -> None:
        """
        모든 unittest 직후에 이 메서드가 호출됩니다.
        """

    def test_v2v(self):
        async def __job():
            v2vp = Video2VideoProcessor(
                input_video_path=config.test_v2v["test_video_url"],
                temp_file_dir=config.PROJECT_DIR,
                output_video_path=config.test_v2v["dst_video_audio_path"],
                v2i_ffmpeg_options_output=config.test_v2v["v2i_ffmpeg_options_output"],
                v2a_ffmpeg_options_output=config.test_v2v["v2a_ffmpeg_options_output"],
                i2v_ffmpeg_options_input=config.test_v2v["i2v_ffmpeg_options_input"],
                i2v_ffmpeg_options_output=config.test_v2v["i2v_ffmpeg_options_output"],
                va2v_ffmpeg_options_output=config.test_v2v[
                    "va2v_ffmpeg_options_output"
                ],
            )
            await v2vp.async_run()

        asyncio.run(__job())
        for path in [
            config.test_v2v["dst_video_audio_path"],
        ]:
            os.remove(path=path)
