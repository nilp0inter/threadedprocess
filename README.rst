ThreadedProcessPoolExecutor
===========================

.. image:: https://img.shields.io/pypi/v/threadedprocess.svg
    :target: https://pypi.python.org/pypi/threadedprocess

.. image:: https://img.shields.io/pypi/l/threadedprocess.svg
    :target: https://pypi.python.org/pypi/threadedprocess

.. image:: https://img.shields.io/pypi/pyversions/threadedprocess.svg
    :target: https://pypi.python.org/pypi/threadedprocess

.. image:: https://travis-ci.org/nilp0inter/threadedprocess.svg?branch=master
    :target: https://travis-ci.org/nilp0inter/threadedprocess


The `ThreadedProcessPoolExecutor` class is an `Executor` subclass that uses a
pool of process with an inner pool of threads on each process to execute calls
asynchronously.


.. class:: ThreadedProcessPoolExecutor(max_processes=None, max_threads=None)

   An `Executor` subclass that is formed by a modified `ProcessPoolExecutor`
   that generates at most *max_processes* processes that use a
   `ThreadPoolExecutor` (with at most *max_threads*) to instance to run the
   given tasks.

   If *max_processes* is ``None`` or not given, it will default to the number
   of processors on the machine.

   If *max_threads* is ``None`` or not given, it will default to the number of
   processors on the machine, multiplied by ``5``.


ThreadedProcessPoolExecutor Example
-----------------------------------

.. code-block:: python

   import math
   import requests
   
   from threadedprocess import ThreadedProcessPoolExecutor
   
   
   RNGURL = "https://www.random.org/integers/?num=1&min=1&max=100000000&col=1&base=10&format=plain&rnd=new"
   
   def get_prime():
       n = int(requests.get(RNGURL).text)
   
       if n % 2 == 0:
           return (n, False)
   
       sqrt_n = int(math.floor(math.sqrt(n)))
       for i in range(3, sqrt_n + 1, 2):
           if n % i == 0:
               return (n, False)
       return (n, True)
   
   futures = []
   
   with ThreadedProcessPoolExecutor(max_processes=4, max_threads=16) as executor:
       for _ in range(128):
           futures.append(executor.submit(get_prime))
   
   for future in futures:
       print('%d is prime: %s' % future.result())
