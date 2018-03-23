import os
import threading
import time

import pytest

from threadedprocess import ThreadedProcessPoolExecutor


def _get_pid_and_tid():
    return (os.getpid(), threading.current_thread().ident)


def _long_running_task():
    start = time.time()
    time.sleep(1)
    end = time.time()
    return (start, end)


def test_futures_run_in_different_processes_and_threads():
    futures = []

    with ThreadedProcessPoolExecutor(max_processes=4,
                                     max_threads=4) as executor:
        for i in range(1000):
            futures.append(executor.submit(_get_pid_and_tid))

    pids_and_tids = {f.result() for f in futures}

    assert len(pids_and_tids) == 16  # 4 processes, 4 threads


@pytest.mark.wip
def test_all_futures_execute_in_parallel_if_possible():
    """
    0....1....2....3....4....5....6....7....8....9
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

    with ThreadedProcessPoolExecutor(max_processes=4,
                                     max_threads=4) as executor:
        for i in range(16):
            futures.append(executor.submit(_long_running_task))

    times = [f.result() for f in futures]
    As, Bs = [t[0] for t in times], [t[1] for t in times]

    assert min(Bs) >= max(As)
