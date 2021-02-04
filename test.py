import logging
import threading
import time

def fib(n):
    if n <= 2: return 1
    else: return fib(n-1) + fib(n-2)

def thread_function(name):
    # logging.info("Thread %s: starting", name)
    fib(35)  ## Change this line of code to fib(20)
    # logging.info("Thread %s: finishing", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    start = time.time()
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = list()
    for index in range(3):
        # logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=thread_function, args=(index,))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        # logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)
    end = time.time()
    print(f'total time: {end-start}')