import threading, warnings

def a():
    for i in range(10**20): 
        x = 1 + 3

def b(): 
    for i in range(10**7): 
        x = 4 + 4
    raise Exception("DONE!")

t1 = threading.Thread(target=a)
t2 = threading.Thread(target=b)


t1.start()
t2.start()

