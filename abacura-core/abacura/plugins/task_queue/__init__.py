"""
Command Queue running routines

Tracks last command, calculates delay, and issues commands in priority order,
depending on the combat situation.
"""

import bisect
import itertools
from dataclasses import dataclass, field
from time import monotonic
from typing import Callable, Optional

from textual import log

from abacura.plugins.events import AbacuraMessage


class InvalidQueueName(Exception):
    pass


_DEFAULT_PRIORITY = 50
_DEFAULT_DURATION: float = 1.0


@dataclass
class TaskQueue:
    priority: int = _DEFAULT_PRIORITY
    insert_check: Callable = lambda: True

    @property
    def insertable(self):
        return self.insert_check()


id_generator = itertools.count(0)


@dataclass()
class Task:
    id: int = field(default_factory=lambda: next(id_generator), init=False)
    cmd: str = ""
    q: str = "any"
    priority: int = _DEFAULT_PRIORITY
    dur: float = 1.0
    delay: float = 0
    timeout: float = 0
    exclusive: bool = False
    queued_time: float = field(default_factory=monotonic)
    insert_check: Callable = lambda: True
    _wait_prior: Optional["Task"] = None
    _inserted: bool = field(default=False, init=True)
    _queue: TaskQueue = field(default_factory=TaskQueue, init=True)

    def __hash__(self):
        return self.id

    @property
    def remaining_delay(self) -> float:
        return float(max(0.0, self.delay + self.queued_time - monotonic()))

    @property
    def timed_out(self) -> bool:
        return 0 < self.timeout < (monotonic() - self.queued_time)

    @property
    def insertable(self):
        checks = [
            self.remaining_delay == 0,
            self._queue.insertable,
            self.insert_check(),
            self._wait_prior is None or self._wait_prior._inserted,
        ]

        return all(checks)

    @property
    def overall_priority(self):
        return self._queue.priority, self.priority, self.id

    def __lt__(self, other):
        return self.overall_priority < other.overall_priority

    def set_queue(self, queue: TaskQueue) -> None:
        self._queue = queue

    @property
    def inserted(self):
        return self._inserted

    @inserted.setter
    def inserted(self, value: bool) -> None:
        self._inserted = value

    @property
    def wait_prior(self):
        return self._wait_prior

    @wait_prior.setter
    def wait_prior(self, value: "Task") -> None:
        self._wait_prior = value


@dataclass
class CQMessage(AbacuraMessage):
    event_type: str = "lok.cqmessage"
    value: str = ""
    tasks: list[Task] = field(default_factory=list)
    next_command_delay: float = 0


class TaskManager:
    """Manage tasks by priority"""

    def __init__(self, queues: dict[str, TaskQueue] | None = None) -> None:
        self.tasks: list[Task] = []
        self._NEXT_COMMAND_TIME: float = 0.0
        self._command_inserter: Callable | None = None
        self._queues: dict[str, TaskQueue] = {}

        if queues:
            self._queues = queues

    @property
    def next_command_delay(self) -> float:
        return max(0.0, self._NEXT_COMMAND_TIME - monotonic())

    def set_command_inserter(self, f: Callable) -> None:
        self._command_inserter = f

    def set_queues(self, queues: dict[str, TaskQueue]) -> None:
        self._queues = queues

        # update queues for each task and re-sort in case priorities changed
        for task in self.tasks:
            task._queue = queues.get(task.q, TaskQueue())

        self.tasks.sort()

    def _get_next_insertable_task(self) -> Task | None:
        # Process these in queue priority order
        for i, task in enumerate(self.tasks):
            if not task.insertable:
                continue

            # Note, popping mutates the list we are iterating, but we are returning so no problem...
            self.tasks.pop(i)
            return task

        return None

    def run_tasks(self) -> None:
        """This is the actual queue runner routine"""

        if self._command_inserter is None:
            log.error("No command inserter")
            return

        self._remove_timeouts()

        # process as many tasks as we can
        while self._NEXT_COMMAND_TIME < monotonic():
            task = self._get_next_insertable_task()
            if task is None:
                break

            self._command_inserter(task.cmd)
            task.inserted = True
            log(f"Sent {task.cmd} inserted at {monotonic()}")
            self._NEXT_COMMAND_TIME = monotonic() + task.dur

    def flush(self, q: str = "") -> None:
        if q == "":
            self.tasks = []
            return

        removals = set(task for task in self.tasks if task.q.lower() == q.lower())
        self._remove_tasks(removals)

    def add_task(self, task: Task) -> None:
        task.set_queue(self._queues.get(task.q, TaskQueue()))

        if task.exclusive:
            check = set(t for t in self.tasks if t.cmd.lower() == task.cmd.lower())
            if check:
                return

        task.inserted = False
        task.queued_time = monotonic()
        bisect.insort(self.tasks, task)
        # self._pq.put(task)
        self.run_tasks()

    def add_chain(self, *tasks) -> None:
        prior = None
        for task in tasks:
            task._wait_prior = prior
            task.set_queue(self._queues.get(task.q, TaskQueue()))
            task.queued_time = monotonic()
            task.inserted = False
            bisect.insort(self.tasks, task)
            prior = task

        self.run_tasks()

    def add(
        self,
        cmd: str,
        q: str = "any",
        priority: int = _DEFAULT_PRIORITY,
        dur: float = _DEFAULT_DURATION,
        delay: float = 0,
        timeout: float = 0,
    ) -> None:
        self.add_task(Task(cmd=cmd, priority=priority, dur=dur, delay=delay, q=q, timeout=timeout))

    def remove(self, cmd: str) -> None:
        removals = set(task for task in self.tasks if task.q.lower() == cmd.lower())
        self._remove_tasks(removals)

    def _remove_tasks(self, removals: set[Task]) -> None:
        """Remove a set of tasks and clear tasks with related priors"""
        self.tasks = [task for task in self.tasks if task not in removals]
        # clear out any priors that got removed
        for task in self.tasks:
            if task.wait_prior in removals:
                task.wait_prior = None

    def _remove_timeouts(self) -> None:
        timeouts = set()
        for task in self.tasks:
            if task.timed_out:
                timeouts.add(task)
                log(f"Task timed out: {task.cmd}@{task.timeout}s")

        self._remove_tasks(timeouts)
