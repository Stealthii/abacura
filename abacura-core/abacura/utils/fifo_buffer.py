from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar("T")


class FIFOBuffer(Generic[T]):
    """Hold a buffer of objects in memory,
    expelling the first entries when exceeding a maximum size"""

    def __init__(self, max_size: int = 16384) -> None:
        self._entries: list[T] = []
        self._max_size = max_size
        self.entry_id: int = 0

    def __getitem__(self, k) -> T:
        return self._entries.__getitem__(k)

    def __len__(self) -> int:
        return len(self._entries)

    def remove_first(self, n: int = 1) -> None:
        self._entries = self._entries[n:]

    def append(self, entry: T) -> None:
        self._entries.append(entry)
        if len(self._entries) > self._max_size:
            # remove a large chunk if we hit the max size for efficiency
            self.remove_first(self._max_size // 16)
        self.entry_id += 1


class TimestampedBuffer(FIFOBuffer):
    def __init__(self, max_size: int = 16384) -> None:
        super().__init__(max_size)
        self.timestamps: list[datetime] = []

    def remove_first(self, n: int = 1) -> None:
        super().remove_first(n)
        self.timestamps = self.timestamps[n:]

    def append(self, entry: object, dt: datetime = None) -> None:
        if dt is None:
            dt = datetime.utcnow()
        self.timestamps.append(dt)
        super().append(entry)
