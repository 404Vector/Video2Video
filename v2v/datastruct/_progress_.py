import threading


class ThreadSafeProgress:
    def __init__(self, tag: str, max_progress: int) -> None:
        self._lock = threading.Lock()
        self._tag = tag
        self._progress = 0
        self._max_progress = max_progress

    def change(self, delta: int):
        lock = self._lock
        lock.acquire()
        self._progress += delta
        lock.release()

    @property
    def progress(self):
        lock = self._lock
        lock.acquire()
        progress = self._progress
        lock.release()
        return progress

    @property
    def max_progress(self):
        return self._max_progress

    @property
    def to_percent(self):
        return 100.0 * self.progress / self.max_progress


__all__ = [
    ThreadSafeProgress.__name__,
]
