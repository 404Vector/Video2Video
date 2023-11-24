from dataclasses import dataclass
import time
from typing import Any, Dict, List
from threading import Thread
import multiprocessing as mp
import numpy as np
import random
import queue


@dataclass
class QueueItem:
    item: Any
    id: int


class ProcessorManagerState:
    in_job_progress: int = 0
    organize_job_progress: int = 0
    out_job_progress: int = 0
    is_enqueue_end = False
    is_dequeue_end = False
    organizer_temp_map: Dict[int, QueueItem] = {}


def task_generate_frame(number_of_jobs: int, in_queue: mp.Queue):
    frame = np.zeros((108, 1920, 3), np.uint8)
    for i in range(number_of_jobs):
        item = QueueItem(frame, id=i)
        in_queue.put(item)
        print(f"task_generate_frame::put {item.id}")
    in_queue.put(QueueItem(None, id=-1))


def task_processing(
    id: int,
    in_queue: mp.Queue,
    out_queue: mp.Queue,
    proc_time: float,
    proc_time_rand: float,
):
    while True:
        item: QueueItem = in_queue.get()
        print(f"processor[{id}]::proc | {item.id}")
        proc_time = proc_time + max(0, proc_time_rand * (random.random() - 0.5))
        time.sleep(proc_time)
        out_queue.put(item)


def task_processor_inqueue(
    state: ProcessorManagerState,
    in_queue: mp.Queue,
    proc_in_queue: mp.Queue,
    proc_out_queue: mp.Queue,
):
    print("task_processor_inqueue::start")
    in_queue_data = None
    while True:
        in_queue_data: QueueItem = in_queue.get()
        state.in_job_progress += 1
        if in_queue_data.item is not None:
            proc_in_queue.put(in_queue_data)
        else:
            assert in_queue_data.id < 0
            proc_out_queue.put(in_queue_data)
            break
    state.is_enqueue_end = True
    print("task_processor_inqueue::end")


def task_processor_dequeue(
    state: ProcessorManagerState,
    proc_out_queue: mp.Queue,
    local_organize_queue: queue.Queue,
):
    print("task_processor_dequeue::start")
    while True:
        out_queue_data: QueueItem = proc_out_queue.get()
        state.out_job_progress += 1
        if out_queue_data.item is None:
            assert out_queue_data.id < 0
            if state.in_job_progress != state.out_job_progress:
                state.out_job_progress -= 1
                proc_out_queue.put(out_queue_data)
                continue
            else:
                local_organize_queue.put(out_queue_data)
                break
        local_organize_queue.put(out_queue_data)
    state.is_dequeue_end = True
    print("task_processor_dequeue::end")


def task_organize_results(
    state: ProcessorManagerState,
    local_organize_queue: queue.Queue,
    out_queue: mp.Queue,
):
    print("task_organize_results::start")
    org_temp_map = {}
    while True:
        item: QueueItem = local_organize_queue.get()
        temp_map = org_temp_map
        if out_queue.full():
            local_organize_queue.put(item)
            print("task_organize_results:skip | the queue is full")
            continue
        state.organize_job_progress += 1
        if item.item is None:
            if state.out_job_progress != state.organize_job_progress:
                state.organize_job_progress -= 1
                local_organize_queue.put(item)
                continue
            else:
                out_queue.put(item)
                break
        key = item.id
        assert key > -1
        temp_map[key] = item
        target_key = state.organize_job_progress - 1
        while target_key in temp_map:
            target_item = temp_map.pop(target_key)
            out_queue.put(target_item)
            print(f"task_organize_results::put | item={target_item.id}")
            target_key += 1
    print("task_organize_results::end")


def task_manage_processors(
    number_of_process: int,
    in_queue: mp.Queue,
    out_queue: mp.Queue,
    proc_time: float,
    proc_time_rand: float,
):
    print("processor_manager::ready")
    state = ProcessorManagerState()
    _proc_in_queue = mp.Queue(number_of_process)
    _proc_out_queue = mp.Queue(number_of_process)
    _proc_organize_queue = queue.Queue(number_of_process)
    processor_process_array = [
        mp.Process(
            target=task_processing,
            args=(id, _proc_in_queue, _proc_out_queue, proc_time, proc_time_rand),
        )
        for id in range(number_of_process)
    ]
    print("processor_manager::start")
    [p.start() for p in processor_process_array]
    print("processor_manager::i/o")
    procs = [
        Thread(
            target=task_processor_inqueue,
            args=(state, in_queue, _proc_in_queue, _proc_out_queue),
        ),
        Thread(
            target=task_processor_dequeue,
            args=(state, _proc_out_queue, _proc_organize_queue),
        ),
        Thread(
            target=task_organize_results,
            args=(state, _proc_organize_queue, out_queue),
        ),
    ]
    [p.start() for p in procs]
    [p.join() for p in procs]

    print("processor_manager::in_queue finished.")
    [p.kill() for p in processor_process_array]
    print("processor_manager::end")


def task_spanding(out_queue: mp.Queue):
    while True:
        item: QueueItem = out_queue.get()
        print(f"spander::get | item={item.id}")
        if item.item is None:
            print(f"spander::END")
            break


def main():
    number_of_jobs = 1000
    number_of_process = 15 * 2
    io_queue_size = number_of_process * 2
    proc_time = 0.02
    proc_time_rand = proc_time * 0.05
    in_queue = mp.Queue(io_queue_size)
    out_queue = mp.Queue(io_queue_size)
    job_maker_process = mp.Process(
        target=task_generate_frame, args=(number_of_jobs, in_queue)
    )
    processor_process = mp.Process(
        target=task_manage_processors,
        args=(number_of_process, in_queue, out_queue, proc_time, proc_time_rand),
    )
    spander_process = mp.Process(
        target=task_spanding,
        args=(out_queue,),
    )
    start = time.time()
    job_maker_process.start()
    processor_process.start()
    spander_process.start()
    spander_process.join()
    processor_process.join()
    job_maker_process.join()

    end = time.time()
    total_time = end - start
    ideal_time = (number_of_jobs / number_of_process) * proc_time
    print(
        f"Test End | Total Time = {total_time:.3f}[sec] | Ideal Time = {ideal_time:.3f} | Error = {(100. *(total_time-ideal_time))/ideal_time:.3f}%"
    )


if __name__ == "__main__":
    main()
