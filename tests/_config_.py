import os
import v2v

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

PUBLIC_TEST_VIDEO_INFO = {
    "description": "Tears of Steel was realized with crowd-funding by users of the open source 3D creation tool Blender. Target was to improve and test a complete open and free pipeline for visual effects in film - and to make a compelling sci-fi film in Amsterdam, the Netherlands.  The film itself, and all raw material used for making it, have been released under the Creatieve Commons 3.0 Attribution license. Visit the tearsofsteel.org website to find out more about this, or to purchase the 4-DVD box with a lot of extras.  (CC) Blender Foundation - http://www.tearsofsteel.org",
    "sources": [
        "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
    ],
    "subtitle": "By Blender Foundation",
    "thumb": "images/TearsOfSteel.jpg",
    "title": "Tears of Steel",
}

TEST_VIDEO_URL = PUBLIC_TEST_VIDEO_INFO["sources"][-1]

test_v2ip = {
    "test_video_url": TEST_VIDEO_URL,
    "ffmpeg_options_output": {
        # trim 3 frames from source
        "ss": "00:01:00",
        "t": "00:00:00.1",
    },
}

test_v2ap = {
    "test_video_url": TEST_VIDEO_URL,
    "ffmpeg_options_output": None,
    "dst_audio_path": os.path.join(PROJECT_DIR, "_TEMP_AUDIO_FOR_TEST_.m4a"),
}

test_i2vp = {
    "test_video_width": 640,
    "test_video_height": 480,
    "test_video_fps": 20,
    "test_video_color_sequence": [
        (r, g, b)
        for r in range(0, 257, 64)
        for g in range(0, 257, 64)
        for b in range(0, 257, 64)
    ],
    "dst_video_path": os.path.join(PROJECT_DIR, "_TEMP_VIDEO_FOR_TEST_.mp4"),
    "ffmpeg_options_input": {},
    "ffmpeg_options_output": {
        "pix_fmt": v2v.FFMPEG_PIX_FMT_YUV420P,
        "b:v": 15000,
    },
}
