import logging
import threading
import time
from fib import fib

n = 0

def thread_function(name):
    global n
    logging.info("Thread %s: starting", name)
    # fib(15)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)
    n += 1

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    start = time.time()
    threads = list()
    for index in range(5):
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=thread_function, args=(index,))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)
    end = time.time()
    print(f'total time: {end-start}')
    print(n)