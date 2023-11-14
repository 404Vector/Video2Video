import unittest
from v2v import Video2ImageProcessor
from . import _config_ as config


class TestVideo2ImageProcessor(unittest.TestCase):
    def setUp(self) -> None:
        """
        모든 unittest 직전에 이 메서드가 호출됩니다.
        """

    def tearDown(self) -> None:
        """
        모든 unittest 직후에 이 메서드가 호출됩니다.
        """

    def test_extract_frames(self):
        v2ip = Video2ImageProcessor(
            video_path=config.test_v2ip["test_video_url"],
            ffmpeg_options_output=config.test_v2ip["ffmpeg_options_output"],
        )
        image_stream = v2ip.create_stream()
        for fid, frame_data in enumerate(image_stream):
            self.assertEqual(fid, frame_data.frame_id)
