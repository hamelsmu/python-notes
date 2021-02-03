import logging
import threading
import time
from fib import fib
from concurrent import futures

n = 0

def thread_function(name):
    global n
    logging.info("Thread %s: starting", name)
    fib(25)
    logging.info("Thread %s: finishing", name)
    n += 1

if __name__ == "__main__":
    start_time = time.time()
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    with futures.ThreadPoolExecutor(max_workers=3) as exec:
        exec.map(thread_function, range(30))
    end_time = time.time()
    print(end_time-start_time)