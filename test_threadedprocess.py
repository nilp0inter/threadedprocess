import os
import threading

from threadedprocess import ThreadedProcessPoolExecutor


def _get_pid_and_tid():
    return (os.getpid(), threading.current_thread().ident)


def test_futures_run_in_different_processes_and_threads():
    futures = []

    with ThreadedProcessPoolExecutor(max_processes=4, max_threads=4) as executor:
        for i in range(1000):
            futures.append(executor.submit(_get_pid_and_tid))

    pids_and_tids = {f.result() for f in futures}

    assert len(pids_and_tids) == 16  # 4 processes, 4 threads
