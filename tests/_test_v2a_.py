import os
import unittest
from v2v import AudioExtractor
from . import _config_ as config


class TestVideo2AudioProcessor(unittest.TestCase):
    def setUp(self) -> None:
        """
        모든 unittest 직전에 이 메서드가 호출됩니다.
        """

    def tearDown(self) -> None:
        """
        모든 unittest 직후에 이 메서드가 호출됩니다.
        """

    def test_extract_audio(self):
        v2ap = AudioExtractor(
            video_path=config.test_v2ap["test_video_url"],
            dst_audio_path=config.test_v2ap["dst_audio_path"],
            ffmpeg_options_output=config.test_v2ap["ffmpeg_options_output"],
        )
        v2ap.run()
        self.assertEqual(
            os.path.exists(v2ap.dst_audio_path),
            True,
            f"{v2ap.dst_audio_path} is not exist!",
        )
        os.remove(v2ap.dst_audio_path)
        self.assertEqual(
            os.path.exists(v2ap.dst_audio_path),
            False,
            f"{v2ap.dst_audio_path} is not deleted!",
        )
