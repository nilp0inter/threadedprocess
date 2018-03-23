import os
from setuptools import setup

try:
    import concurrent.futures
except ImportError:
    CONCURRENT_FUTURES_PRESENT = False
else:
    CONCURRENT_FUTURES_PRESENT = True


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="threadedprocess",
    version="0.0.5",
    author="Roberto Abdelkader Martinez Perez",
    author_email="robertomartinezp@gmail.com",
    description=(
        "A `ThreadedProcessPoolExecutor` is formed by a modified "
        "`ProcessPoolExecutor` that generates processes that use a "
        "`ThreadPoolExecutor` instance to run the given tasks."),
    license="BSD",
    keywords="concurrent futures executor process thread",
    url="https://github.com/nilp0inter/threadedprocess",
    py_modules=['threadedprocess'],
    long_description=read('README.rst'),
    install_requires=[] if CONCURRENT_FUTURES_PRESENT else ["futures"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
