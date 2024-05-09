import sys
import threading
from collections import deque
from dataclasses import dataclass
from time import perf_counter_ns

try:
    from resource import RUSAGE_SELF, getrusage
except ImportError:
    from typing import NamedTuple

    # Define the struct_rusage as a namedtuple with fields similar to Unix's getrusage output
    struct_rusage = NamedTuple(
        "struct_rusage",
        [
            ("ru_utime", float),  # user CPU time used
            ("ru_stime", float),  # system CPU time used
            ("ru_maxrss", int),  # maximum resident set size
            ("ru_ixrss", int),  # integral shared memory size
            ("ru_idrss", int),  # integral unshared data size
            ("ru_isrss", int),  # integral unshared stack size
            ("ru_minflt", int),  # page reclaims (soft page faults)
            ("ru_majflt", int),  # page faults (hard page faults)
            ("ru_nswap", int),  # swaps
            ("ru_inblock", int),  # block input operations
            ("ru_oublock", int),  # block output operations
            ("ru_msgsnd", int),  # messages sent
            ("ru_msgrcv", int),  # messages received
            ("ru_nsignals", int),  # signals received
            ("ru_nvcsw", int),  # voluntary context switches
            ("ru_nivcsw", int),  # involuntary context switches
        ],
    )

    RUSAGE_SELF = 0

    def getrusage(__who: int, /) -> struct_rusage:
        # on non-UNIX platforms cpu_time always 0.0
        return struct_rusage(0.0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


@dataclass(slots=True, frozen=True, eq=True)
class Function:
    co_name: str = ""
    co_filename: str = ""
    co_first_lineno: int = 0

    def get_location(self) -> str:
        return f"{self.co_filename}:{self.co_name}[{self.co_first_lineno}]"


@dataclass(slots=True)
class FunctionStats:
    function: Function
    call_count: int = 0
    elapsed_time: float = 0
    cpu_time: float = 0
    child_time: float = 0
    child_cpu_time: float = 0

    @property
    def self_time(self) -> float:
        return self.elapsed_time - self.child_time

    @property
    def self_cpu_time(self) -> float:
        return self.cpu_time - self.child_cpu_time


@dataclass(slots=True)
class FunctionCall:
    function: Function = Function()
    start_time: float = 0
    start_cpu_time: float = 0
    child_time: float = 0
    child_cpu_time: float = 0


p_stats: dict[Function, FunctionStats] = {}
p_start_time = None
p_profiling = False


def profiler(frame, event, _arg):
    global p_stats
    if event not in ("call", "return"):
        return profiler

    # gather stats
    rusage = getrusage(RUSAGE_SELF)
    t_cpu = rusage[0] + rusage[1]  # user time + system time
    code = frame.f_code
    function = Function(code.co_name, code.co_filename, code.co_firstlineno)

    # get stack with functions entry stats
    ct = threading.current_thread()
    try:
        p_stack = ct.p_stack
    except AttributeError:
        ct.p_stack = deque()
        p_stack = ct.p_stack

    # handle call and return #
    if event == "call":
        p_stack.append(FunctionCall(function, perf_counter_ns(), t_cpu))
        return profiler

    # return
    try:
        function_call: FunctionCall = p_stack.pop()
        assert function_call.function == function
    except IndexError:
        # TODO investigate
        return profiler

    if function in p_stats:
        function_stats = p_stats[function]
    else:
        function_stats = FunctionStats(function)
        p_stats[function] = function_stats

    call_time = perf_counter_ns() - function_call.start_time
    cpu_time = t_cpu - function_call.start_cpu_time
    function_stats.call_count += 1
    function_stats.elapsed_time += call_time
    function_stats.cpu_time += cpu_time
    function_stats.child_time += function_call.child_time
    function_stats.child_cpu_time += function_call.child_cpu_time

    if len(p_stack):
        parent: FunctionCall = p_stack[-1]
        parent.child_time += call_time
        parent.child_cpu_time += cpu_time

    return profiler


def profile_on() -> None:
    global p_stats, p_start_time, p_profiling
    p_stats = {}
    p_start_time = perf_counter_ns()
    threading.setprofile(profiler)
    sys.setprofile(profiler)
    p_profiling = True


def profile_off() -> None:
    global p_profiling
    threading.setprofile(None)
    sys.setprofile(None)
    p_profiling = False


def get_profile_stats() -> dict[Function, FunctionStats]:
    """
    returns dict[Function] -> FunctionStats
    """
    return p_stats
