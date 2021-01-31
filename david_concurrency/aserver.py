from socket import *
from fib import fib 
from threading import Thread
from concurrent.futures import ProcessPoolExecutor as Pool
from collections import deque
from select import select
pool = Pool(4)

tasks = deque()
recv_wait = { }
send_wait = { }

def run():
    while any([tasks, recv_wait, send_wait]):
        while not tasks:
            #No active tasks to run
            # wait for I/O
            can_recv, can_send, [] = select(recv_wait, send_wait, [])
            for s in can_recv:
                tasks.append(recv_wait.pop(s))
            for s in can_send:
                tasks.append(send_wait.pop(s))
        task = tasks.popleft()
        try:
            why,what=next(task)
            if why == 'recv':
                #Must go wait somewhere
                recv_wait[what] = task
            elif why == 'send':
                send_wait[what] = task
            else:
                raise RuntimeError("ARG!")
        except StopIteration:
            print ("task done")

def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    sock.bind(address)
    sock.listen(5)
    while True:
        yield 'recv', sock
        client,addr = sock.accept()  #blocking per connection, waits for a connection to occur.
        print("Connection", addr)
        tasks.append(f ib_handler(client))
        # Thread(target=fib_handler, args=(client,), daemon=True).start() # Creates a new thread per connection.  See below for why this is important.
        
def fib_handler(client):
    while True:
        yield 'recv', client
        req = client.recv(100)  #blocking ** this line really blocks and waits for the next request, it continues to block in the thread. If this is not in a thread, you cannot have another connectino
        if not req: break
        result = fib(int(req))
        # future = pool.submit(fib, n)  # this executes the fibonnnaci function in another process so its not competing for resources on this thread
        # result = future.result() # this is part of how pool works, we are fetching the result.
        resp = str(result).encode('ascii') + b'\n'
        yield 'send', client
        client.send(resp) # this might block too, if send buffers are full.
    print("Closed")
    
tasks.append(fib_server(('', 25000)))
run()