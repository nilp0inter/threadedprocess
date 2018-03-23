import os
import threading
import time

import pytest

from threadedprocess import ThreadedProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def _get_pid_and_tid():
    return (os.getpid(), threading.current_thread().ident)


def _long_running_task(*_):
    start = time.time()
    time.sleep(1)
    end = time.time()
    return (start, end)


def _return_True():
    return True


def _raise_ValueError():
    raise ValueError


def test_futures_run_in_different_processes_and_threads():
    """
    Check that all spawned processes and threads are used to run the submitted
    tasks.

    """
    futures = []

    with ThreadedProcessPoolExecutor(max_processes=4,
                                     max_threads=4) as executor:
        for i in range(1000):
            futures.append(executor.submit(_get_pid_and_tid))

    pids_and_tids = set((f.result() for f in futures))

    assert len(pids_and_tids) == 16  # 4 processes, 4 threads


def test_results_return():
    with ThreadedProcessPoolExecutor() as executor:
        f = executor.submit(_return_True)

    assert f.result() is True


def test_exceptions_raises():
    with ThreadedProcessPoolExecutor() as executor:
        f = executor.submit(_raise_ValueError)

    with pytest.raises(ValueError):
        assert f.result()


@pytest.mark.parametrize("EXECUTOR", [
    ProcessPoolExecutor(max_workers=16),
    ThreadPoolExecutor(max_workers=16),
    ThreadedProcessPoolExecutor(max_processes=4, max_threads=4)
])
def test_all_futures_execute_in_parallel_if_possible(EXECUTOR):
    """
    If the number of tasks submitted to the executor is lower than the number
    of workers the executor has, all the tasks should run concurrently (given
    the task running time is not too short).

    0....1....2....3....4....5....6....7
    # DO OVERLAP
         A-----------------B
           A----B
               A----B
              A----B

    # DON'T OVERLAP
         A-----------------B
           A---B
                A----B
              A----B

    """
    futures = []

    with EXECUTOR as executor:
        for i in range(16):
            futures.append(executor.submit(_long_running_task))

    times = [f.result() for f in futures]
    As, Bs = [t[0] for t in times], [t[1] for t in times]

    assert min(Bs) >= max(As)
