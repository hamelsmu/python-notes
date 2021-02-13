from threading import Thread

def foo():
	for i in range(1000000): 
		sum([(100*12341 + 99) for i in range(10**30)]) + sum([(100*12341 + 99) for i in range(10**30)]) + sum([(100*12341 + 99) for i in range(10**3)])

for i in range(23): Thread(target=foo).start()
