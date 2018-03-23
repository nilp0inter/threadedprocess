"""Implements ThreadedProcessPoolExecutor.

A `ThreadedProcessPoolExecutor` is formed by a modified `ProcessPoolExecutor`
that generates processes that use a `ThreadPoolExecutor` instance to run the
given tasks.

"""
__author__ = 'Roberto Abdelkader Martínez Pérez (robertomartinezp@gmail.com)'

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures import _base
from concurrent.futures.process import _ExceptionWithTraceback, _ResultItem
from concurrent.futures.thread import _shutdown, _threads_queues
from functools import partial
import multiprocessing
import os
import threading
import weakref


def _worker(executor_reference, work_queue, available_thread):
    try:
        while True:
            work_item = work_queue.get(block=True)
            if work_item is not None:
                work_item.run()
                available_thread.release()
                # Delete references to object. See issue16284
                del work_item
                continue
            else:
                available_thread.release()

            executor = executor_reference()
            # Exit if:
            #   - The interpreter is shutting down OR
            #   - The executor that owns the worker has been collected OR
            #   - The executor that owns the worker has been shutdown.
            if _shutdown or executor is None or executor._shutdown:
                # Notice other workers
                work_queue.put(None)
                return
            del executor
    except BaseException:
        _base.LOGGER.critical('Exception in worker', exc_info=True)


class _ThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None):
        super(_ThreadPoolExecutor, self).__init__(max_workers)
        self._available_thread = threading.Semaphore(self._max_workers)

    def _adjust_thread_count(self):
        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)
        # TODO(bquinlan): Should avoid creating new threads if there are more
        # idle threads than items in the work queue.
        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = '%s_%d' % (self, num_threads)
            t = threading.Thread(name=thread_name, target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue,
                                       self._available_thread))
            t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue


def _return_result(call_item, result_queue, future):
    try:
        r = future.result()
    except BaseException as e:
        exc = _ExceptionWithTraceback(e, e.__traceback__)
        result_queue.put(_ResultItem(call_item.work_id, exception=exc))
    else:
        result_queue.put(_ResultItem(call_item.work_id, result=r))


def _process_worker(max_threads, call_queue, result_queue):
    """Evaluates calls from call_queue and places the results in result_queue.

    This worker is run in a separate process.

    Args:
        call_queue: A multiprocessing.Queue of _CallItems that will be read and
            evaluated by the worker.
        result_queue: A multiprocessing.Queue of _ResultItems that will written
            to by the worker.
        shutdown: A multiprocessing.Event that will be set as a signal to the
            worker that it should exit when call_queue is empty.
    """
    with _ThreadPoolExecutor(max_workers=max_threads) as executor:
        while True:
            # Wait for the queue to be empty. Either initial state or a
            # worker got the workitem.

            executor._available_thread.acquire()

            call_item = call_queue.get(block=True)
            if call_item is None:
                # Wake up queue management thread
                result_queue.put(os.getpid())
                return

            future = executor.submit(call_item.fn,
                                     *call_item.args,
                                     **call_item.kwargs)
            future.add_done_callback(
                partial(_return_result, call_item, result_queue))


class ThreadedProcessPoolExecutor(ProcessPoolExecutor):
    def __init__(self, max_processes=None, max_threads=None):
        """Initializes a new ThreadedProcessPoolExecutor instance.

        Args:
            max_processes: The maximum number of processes that can be used. If
                None or not given then as many worker processes will be created
                as the machine has processors.
            max_threads: The maximum number of thread per proces that can be
                used to execute the given calls.
        """
        self.max_processes = max_processes
        self.max_threads = max_threads

        super(ThreadedProcessPoolExecutor, self).__init__(
            max_workers=self.max_processes)

    def _adjust_process_count(self):
        for _ in range(len(self._processes), self._max_workers):
            p = multiprocessing.Process(
                    target=_process_worker,
                    args=(self.max_threads,
                          self._call_queue,
                          self._result_queue))
            p.start()
            self._processes[p.pid] = p
