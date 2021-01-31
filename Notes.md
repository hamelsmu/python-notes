- Learn how threads work.
- Learn how thread pools work and what they are.
- What are coroutines.


- Continue reading RealPython tutorial.  What is a threadpool?  How is that different than a processpool? https://realpython.com/intro-to-python-threading/
- David's talk: https://www.youtube.com/watch?v=MCs5OvhV9S4



Notes

- with threads, stay away from CPU bound work, or they will compete with other threads
- for cpu bound work, offload to a sub - process so you are not competing with the thread.
-  two threads have interleaving access to a single shared object, overwriting each other’s results. Similar race conditions can arise when one thread frees memory or closes a file handle before the other thread is finished accessing it.
- The operating system can swap which thread is running at any time. A thread can be swapped out after any of these small instructions. This means that a thread can be put to sleep to let another thread run in the middle of a Python statement.



=========

Async Talk: https://www.youtube.com/watch?v=E-1Y4kSsAFc

Coroutines don't run themselves, something has to run them.
