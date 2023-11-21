"""
# Video2Video   

Python package for converting video to video with ffmpeg.   

For more information, Visit [the github repository](https://github.com/404Vector/Video2Video)
 
"""
import os


if "GITHUB_ACTION_TAG_NAME" in os.environ:
    __version__ = os.environ["GITHUB_ACTION_TAG_NAME"]
else:
    import datetime

    __version__ = f"0.0.{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y.%m.%d.%H.%M.%S')}"

from .datastruct import *
from .utils import *
from ._video2image_processor_ import *
from ._image2video_processor_ import *
from ._audio_extractor_ import *
from ._audio_merger_ import *
from ._const_ import *
from .interface import *
from ._frame_organizer_ import *
from ._null_frame_processor_ import *
from ._null_frame_processor_pool_ import *
from ._video2video_processor_ import *
