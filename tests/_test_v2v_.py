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
                output_video_path=config.test_v2v["dst_video_audio_path"],
            )
            await v2vp.async_run()

        asyncio.run(__job())
        for path in [
            config.test_v2v["dst_video_audio_path"],
        ]:
            os.remove(path=path)
