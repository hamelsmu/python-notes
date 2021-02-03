---
title: "Python: Threads, Processes and Concurrency"
date: 2020-02-05
url: /
draft: false
description: "Understanding basic python concurrency through realistic examples."
author: "Hamel Husain"
images:
- cpu.jpg
autoCollapseToc: true
---

![](cpu.jpg) Credit:[^4]

### Understand the world of Python concurrency: threads, processes, coroutines and asynchronous programming with a realistic examples.

# Motivation

As [a data scientist who is spending more and more time on software engineering](https://hamel.dev/), I was recently forced to confront an ugly gap in my knowledge of Python: concurrency.  To be honest, I never completely understood how the terms async, threads, pools and coroutines were different and how these mechanisms could work together.  Whenever I encountered talks or material that mentioned these terms, I was unable to grasp related concepts or follow along.

Furthermore, I was guilty of incorrectly applying these mechanisms due to my lack of understanding.  For example, I avoided using threads completely in favor of processes all the time.  Most importantly, every time I tried to learn about the subject, the examples were a bit too abstract for me, and I hard time internalizing how everything worked.  

This changed when a friend of mine, [Jeremy Howard](https://www.fast.ai/about/#jeremy), recommended [a live coding talk](https://youtu.be/MCs5OvhV9S4) by [Daivd Beazley](https://www.dabeaz.com/), an accomplished Python educator.  

_Because of restrictions with this YouTube video, I couldn't embed [the video](https://youtu.be/MCs5OvhV9S4) in this article, so you will have to open it in a different window_.

This talk is incredibly intimidating at first.  Not only is it coded live from scratch, but it also jumps immediately into socket programming, something that I had never encountered as a data scientist.  However, I was encouraged to take things slow and deeply understand this talk, and attempt to understand each piece bit by bit.  This blog post documents what I learned along the way with the hopes that it will benefit others.

# Prerequisites

Before getting started, David sets up the following infrastructure that is used to demonstrate threads and concurrency.

## A cpu-bound task: Fibonacci

To demonstrate concurrency, it is useful to create a task that can saturate your CPU, (such as mathematical operations) for a noticeable period of time.  For this purpose David uses a function that computes a [Fibonacci number](https://en.wikipedia.org/wiki/Fibonacci_number).

```py3
#fib.py
def fib(n):
    if n <= 2: return 1
    else: return fib(n-1) + fib(n-2)
```

This function is useful for threads as it will take much longer for large inputs versus smaller inputs[^1], which allows us to profile different workloads.

## A Simple Web Server

It is also useful to have a real-word task that can benefit from threading.  A web server is one of the best ways to illustrate the benefits of concurrency with both thread and processes.  However, to really demonstrate how things work it is useful to use something that is sufficiently low level enough to see how the pieces work.

For this, David sets up a web server using socket programming.  If you aren't familiar with socket programming (I'm willing to bet most people are not), please stop reading and complete [this tutorial](https://ruslanspivak.com/lsbaws-part1/).

To begin with, David starts with the below code (I've highlighted the most interesting bits):

```py3 {hl_lines=[11,13,17,21]}
# server-1.py
from socket import *
from fib import fib 

def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client,addr = sock.accept()  # waits for a connection to be established
        print("Connection", addr)
        fib_handler(client) # passes the client to a handler which will listen for input data.
        
def fib_handler(client):
    while True:
        req = client.recv(100)  # waits for data that sent by the client.
        if not req: break
        result = fib(int(req))
        resp = str(result).encode('ascii') + b'\n'
        client.send(resp) # sends data back to the client.
    print("Closed")
    
fib_server(('', 25000))
```
Here is an explanation of this code:

- Lines 6-9 are socket programming boilerplate.  It's ok to just take this for granted as a reasonable way to set up a socket server.  This also matches the [the tutorial](https://ruslanspivak.com/lsbaws-part1/) I linked to above.
- Line 11 waits for an incoming connection from a client.  Once a connection is made, the server can begin receiving data from a client.  The code will stop execution on this line until a connection is made.
- Line 13: Once a connection is established, the client object is passed to a function which can handle data sent by the client.
- Line 17: waits for data to be sent by the client.  The code will stop execution on this line until data is received from the client.
- Line 21: The server sends a response back to the client.  The code _could_ stop execution on this line if the send buffers are full, but unlikely in this toy example.

# Testing the non-concurrent code

In the above example, the server will only be able to accept a connection from a single client, because the call to `fib_handler` will never return (because it will run in an infinite loop unless a kill signal is received) which means that `sock.accept()` can only be called once.

You can test this out by first running the server:
> python server-1.py

Then establish a client:
> telnet localhost 25000

You can type numbers in [as David does in his video](https://youtu.be/MCs5OvhV9S4?t=293) and verifies that fibonacci numbers are returned.  However, if you try to connect with another client at the same time from a different terminal session:
> telnet localhost 25000

You will notice that the second client just hangs and doesn't return anything from the server.  This is because the server is only able to accept a single connection.  We can solve this with threads:

# Threads

A way to solve this issue is to use threads.  If you haven't encountered threads before, please go through [this tutorial on threads](https://realpython.com/intro-to-python-threading/).  

You can add threads to the handler so that more connections can be accepted by adding the following two lines code highlighted in yellow:

```py {hl_lines=[3,13]}
from socket import *
from fib import fib
from threading import Thread

def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client,addr = sock.accept()
        print("Connection", addr)
        Thread(target=fib_handler, args=(client,)).start()
        
def fib_handler(client):
    while True:
        req = client.recv(100) 
        if not req: break
        result = fib(int(req))
        resp = str(result).encode('ascii') + b'\n'
        client.send(resp)
    print("Closed")
    
fib_server(('', 25000))
```

You can verify that this works by connecting two separate clients to the server by running the following command in two separate terminal shells: 
> telnet localhost 25000

By executing the `fib_handler` in a thread, the main while loop in `fib_server` will continue, allowing `sock.accept()` to receive additional clients.  

## Thread performance & the GIL

When code stops execution and waits for an external event to occur (like a connection to be made, or data to be sent), this is often referred to as [blocking](https://stackoverflow.com/questions/2407589/what-does-the-term-blocking-mean-in-programming).

One important utility of Python threads is that it allows you to force blocking process to share CPU resources better.  However, Python thread's share a single CPU due to Python's [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock) (GIL).  

Therefore, you have to think carefully about what kind of tasks you execute on threads.  If you try to execute CPU bound tasks the tasks will compete with each other and slow each other down.  David demonstrates this with this script that sends a bunch of requests to our threaded server:

```py
#perf1.py
from socket import *
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 25000))

while True:
    start = time.time()
    sock.send(b'30')
    resp = sock.recv(100)
    end = time.time()
    print(end-start)
```

If you run several instances of this script (after starting the server first):
> python perf1.py

You will see the execution times for each script linearly increase as you increase the number of these scripts running in parallel.  **For this particular task, adding threads does not make anything faster.  But why?**  This is because the fibonacci task is CPU bound so threads will compete with each other for resources on the same CPU core.

Threads work by interleaving the execution of different tasks on your CPU.  Only one thread runs at a time, and take turns executing in small bits until all threads are done. The details of this are carried about by your operating system, so you need not worry about how this happens (with one exception mentioned below). Note that this interleaving doesn't always occur in a predictable way (but is not something you should worry about).  Because you are restricted to a single CPU core in Python, interleaving a bunch of CPU bound tasks will not speed up the total runtime of those tasks.  However, if your tasks involve lots of non-CPU time, such as waiting for network connections, or disk I/O interleaving tasks may result in a considerable speedup.  A canonical way of simulating a non-cpu bound task in python is to use the built-in function `time.sleep()`.  

To check my understanding about threads and performance, I edited [this code](https://realpython.com/intro-to-python-threading/#working-with-many-threads) from the tutorial on threads mentioned to above, and changed `time.sleep(2)` to `fib(20)` and back again:

```py {hl_lines=[7]}
import logging
import threading
import time

def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)  ## Change this line of code to fib(20)
    logging.info("Thread %s: finishing", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    start = time.time()
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = list()
    for index in range(3):
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
```

As expected, increasing the number of threads while running `time.sleep(2)` did not increase the program's overall execution time (the program runs in roughly 2 seconds).  On the other hand, replacing `time.sleep(2)` with `fib(20)` causes this program's running time to increase as more threads are added. This is because `fib(20)` is a cpu bound task so interleaving the task doesn't really help much.

Another interesting but less known aspect that David discusses is the relation between the following two types of tasks:

1. things that take much longer to compute on the CPU, like `fib(30)`, _demonstrated with  [perf1.py](https://github.com/dabeaz/concurrencylive/blob/master/perf1.py)_.
2. things that compute relatively fast on the CPU, like `fib(1)`, _demonstrated with [perf2.py](https://github.com/dabeaz/concurrencylive/blob/master/perf2.py)_.

The Python GIL will prioritize the first type of task at the expense of the second if they are made to compete for resources with threads.  You can follow along with a demonstration of this [here](https://youtu.be/MCs5OvhV9S4?t=568).  This is interesting because this is the opposite of how typical operating systems prioritize threads (by favoring shorter running tasks) and is something unique to the implementation of the Python GIL.  More importantly, this behavior has a very practical consequence: if you are running a web-server where most tasks are fairly quick, one outlier expensive cpu-bound task can grind everything to a halt.

## Threads are not just about making things faster

It is tempting to think of threads as a tool to make things run faster, but that's not the only use case.  Recall that the socket server used threads to allow multiple connections at once without any speedup.  David illustrates another way to use threads with his code used to measure the runtime of short-running tasks: 

[perf2.py](https://github.com/dabeaz/concurrencylive/blob/master/perf2.py):
```py {hl_lines=[12, 19]}
# perf2.py
# requests/sec of fast requests

from socket import *
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 25000))

n = 0

from threading import Thread
def monitor():
    global n
    while True:
        time.sleep(1)
        print(n, 'reqs/sec')
        n = 0
Thread(target=monitor).start()

while True:
    sock.send(b'1')
    resp =sock.recv(100)
    n += 1
```

In this case David uses a single thread with blocking call to `sleep(1)` to make sure that `monitor`  only prints out a metric once per second, while allowing the rest of the program to send requests hundreds of times per second.  In other words, this is a clever use of threads and blocking that allow a part of the program to run at a specified time interval while allowing the rest of your program to run as usual. [^2]  

These different angles of looking at threads allowed me to understand threads more holistically.  Threads are not only about making certain things run faster or run in parallel, but also allows you to control how your program is executed.

# Processes For CPU Bound Tasks

One way to solve the problem with the GIL and cpu-bound tasks competing for resources is to use processes instead of threads.  Processes are different from threads in the following respects:

- Threads share a memory space, whereas processes have a separate memory space.  This is an important consideration if you need to share variables or data between tasks.
- Processes have significant overhead compared to threads because data and program state has to be replicated across each process.
- Unlike threads, processes are not constrained to run on a single CPU, so you can execute cpu-bound tasks in parallel on different cores.

You can learn more about the differences between processes and threads in [this tutorial](https://realpython.com/python-concurrency). David uses python processes in the server by using a process pool.[^3]  The relevant lines of code are highlighted below:

```py {hl_lines=[7, 9, "27-28"]}
# server-3.py
# Fib microservice

from socket import *
from fib import fib
from threading import Thread
from concurrent.futures import ProcessPoolExecutor as Pool

pool = Pool(4)

def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        print("Connection", addr)
        Thread(target=fib_handler, args=(client,), daemon=True).start()

def fib_handler(client):
    while True:
        req = client.recv(100)
        if not req:
            break
        n = int(req)
        future = pool.submit(fib, n)
        result = future.result()
        resp = str(result).encode('ascii') + b'\n'
        client.send(resp)
    print("Closed")

fib_server(('',25000))
```

If you then start this version of the server with:
> python server-3.py

And run the profiler [perf2.py](https://github.com/dabeaz/concurrencylive/blob/master/perf2.py), we can make the following observations:

1. The requests/sec are lower than the thread based version, because there is more overhead required to execute tasks in a pool.
2. However, if you also run [perf1.py](https://github.com/dabeaz/concurrencylive/blob/master/perf1.py) it will not materially interfere with the first task, as this will not compete for resources on the same CPU.

This is a realistic example that allow you to gain more intuition about how threads and processes work.

# Asynchronous programming

Recall that threads run one task at a time, and the operating system automatically decides when to interrupt each thread to allow the threads to take turns running.  This is called [pre-emptive multitasking](https://en.wikipedia.org/wiki/Preemption_%28computing%29#Preemptive_multitasking) since the operating systems, not you, determine when your thread makes the switch.  When you don't care about how tasks are interleaved, threads are great because you don't have to worry about how they are scheduled.

However, there is third type of concurrency paradigm in Python that allows you to control how this switching occurs: Asynchronous Programming.  This is also called [cooperative multitasking](https://en.wikipedia.org/wiki/Cooperative_multitasking) which means each task must announce when it wants to switch. Another term used for cooperative multitasking is a [coroutine](https://www.geeksforgeeks.org/coroutine-in-python/).

One way to create coroutines in Python is by using the `yield` statement.  David provides some intuition on how you can achieve multi-tasking with yield in the following code:

```py
from collections import deque

def countdown(n):
    while n > 0:
        yield n
        n -=1

tasks = deque()
tasks.extend([countdown(10), countdown(5), countdown(20)])

def run():
    while tasks:
        task = tasks.popleft()
        try:
            x=next(task)
            print(x)
            tasks.append(task)
        except StopIteration: print("Task")
```

When you run this code, you can see from the output the three countdown tasks are being interleaved:

```
> run()

10
5
20
9
4
19
8
3
18
...
```

This clever use of `yield` allows you to pause execution of a task and move onto a different task kind of like threading, except **you**, not the operating system are controlling how compute is interleaved.  This is the key intuition for understanding the rest of the talk, which goes on to to push this example further.

One of the most popular ways to accomplish async programming is by using the various utilities in the built-in [asyncio](https://docs.python.org/3/library/asyncio.html) module, which uses similar yield statements under the hood. I didn't end up diving deeply into the asyncio module or this particular flavor of programming as my goal was to understand the concept so that I wouldn't be lost when encountering this in the wild.

# Conclusion

This talk really helped me learn about various concurrency paradigms in Python: threading, processes, and async using coroutines.  I hope that my commentary helps others follow along easier and get the same benefit that I did from it.

# Other random things

In David's code, [deque](https://docs.python.org/3/library/collections.html#collections.deque) from the `collections` module was introduced, which is a very handy data structure not only for async programming but also for threads because they are thread-safe, which means that you don't have to worry about [race conditions](https://realpython.com/intro-to-python-threading/#race-conditions). Similarly, the [queue](https://docs.python.org/3/library/queue.html) module provides other types of thread-safe queues.

Furthermore, one of my favorite python libraries, [fastcore](https://fastcore.fast.ai/), contains a module called [parallel](https://fastcore.fast.ai/parallel.html) which makes using threads and processes easy for many use cases.  

# Resources

- [GitHub repo](https://github.com/dabeaz/concurrencylive) that contains David's code.

[^1]: This fibonacci algorithm runs in O(n<sup>2</sup>) time.
[^2]: If the `monitor` task took any meaningful CPU time then the rest of the program would not run as "usual" because it might be competing for resources.  But that is not the case here.
[^3]: One of the most popular ways of using process pools is with the built-in [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) module.
[^4]: Photo is from Luan Gjokaj on [UnSplash](https://unsplash.com/photos/nsr4hePZGYI).
