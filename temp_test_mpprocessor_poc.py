import os
import time
import v2v
import asyncio
import multiprocessing as mp


PROJECT_DIR = os.path.dirname(__file__)
VIDEO_PATH = os.path.join(PROJECT_DIR, "dist", "1.mp4")
RESULT_VIDEO_PATH = VIDEO_PATH + ".result.mp4"


async def watcher(mp_queue: mp.Queue):
    while True:
        print(f"check:{mp_queue.qsize()}")
        await asyncio.sleep(0.1)


async def main():
    print("start")
    start = time.time()
    mp_queue = mp.Queue(40)
    v2i_engine = v2v.MPVideo2ImageProcessor(
        mp_queue=mp_queue,
        video_path=VIDEO_PATH,
        ffmpeg_options_output=None,
    )
    info = v2v.VideoInfo(v2v.utils.get_video_info_from_path(video_path=VIDEO_PATH))
    i2v_engie = v2v.MPImage2VideoProcessor(
        mp_queue=mp_queue,
        dst_video_path=RESULT_VIDEO_PATH,
        width=info.frame_width,
        height=info.frame_height,
        fps=info.avg_frame_rate,
    )
    v2i_engine.run()
    i2v_engie.run()
    await asyncio.gather(
        # asyncio.create_task(watcher(mp_queue)),
        asyncio.to_thread(v2i_engine.join),
        asyncio.to_thread(i2v_engie.join),
    )
    end = time.time()
    print(f"end | total : {end-start} sec")


if __name__ == "__main__":
    asyncio.run(main())
