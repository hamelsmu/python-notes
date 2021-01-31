from socket import *
from fib import fib 
from threading import Thread
from concurrent.futures import ProcessPoolExecutor as Pool
pool = Pool(4)

def fib_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    sock.bind(address)
    sock.listen(5)
    while True:
        yield 'recv', client
        client,addr = sock.accept()  #blocking per connection, waits for a connection to occur.
        print("Connection", addr)
        Thread(target=fib_handler, args=(client,), daemon=True).start() # Creates a new thread per connection.  See below for why this is important.
        
def fib_handler(client):
    while True:
        yield 'recv', client
        req = client.recv(100)  #blocking ** this line really blocks and waits for the next request, it continues to block in the thread. If this is not in a thread, you cannot have another connectino
        if not req: break
        future = pool.submit(fib, n)  # this executes the fibonnnaci function in another process so its not competing for resources on this thread
        result = future.result() # this is part of how pool works, we are fetching the result.
        resp = str(result).encode('ascii') + b'\n'
        yield 'send', client
        client.send(resp) # this might block too, if send buffers are full.
    print("Closed")
    
fib_server(('', 25000))
