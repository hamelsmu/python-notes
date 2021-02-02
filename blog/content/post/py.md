---
title: "Python: Threads, Processes and Concurrency"
date: 2020-02-05
url: /
draft: false
description: "Understanding basic python concurrency through realistic examples."
author: "Hamel Husain"
autoCollapseToc: true
---

## Motivation

As a data scientist who is spending more and more time on software engineering I was recently forced to confront an ugly gap in my knowledge of Python: threads and processes.  To be honest, I never quite understood how these worked and have been lazily using high level abstractions without a proper understanding of what they meant.  Furthermore, I avoided using threads completely in favor of processes because of my lack of understanding.  

Most importantly, whenever I encountered talks or material that mentioned the terms async, threads and concurrency I was unable to grasp related concepts or follow along.  Furthermore, every
 time I read a book on the subject it was a bit too abstract for me, and I hard time internalizing how everything worked.  

This changed when a friend of mine, [Jeremy Howard](https://www.fast.ai/about/#jeremy) kept recommending this video by [Daivd Beazley](https://www.dabeaz.com/), and accomplished Python educator:

<p align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/MCs5OvhV9S4" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>

This talk is incredibly intimidating at first.  Not only is it coded live from scratch, but it also jumps immediately into socket programming, something that I had never encountered as a data scientist.  However, I was encouraged to take things slow and deeply understand this talk, and attempt to understand each piece bit by bit.  This blog post documents what I learned along the way with the hopes that it will benefit others.

## Pre-requisites

Before getting started, David sets up the following infrastructure that is necessary to demonstrate threads and concurrency.

### A cpu-bound task: Fibonacci

To demonstrate concurrency it is useful to create a task that can saturate your CPU, (such as mathematical operations) for a noticeable period of time.  For this purpose he uses a function that computes a [Fibonacci number](https://en.wikipedia.org/wiki/Fibonacci_number).

```py3
#fib.py
def fib(n):
    if n <= 2: return 1
    else: return fib(n-1) + fib(n-2)
```

### A Simple Web Server

It is also useful to have a real-word task that can benefit from threading.  For reasons discussed later in this blog post, a web server is one of the best ways to illustrate the benefits of concurrency with both thread and processes.  However, to really demonstrate how things work it is useful to use something that is sufficiently low level enough to see how the pieces work.

For this, David sets up a web server using socket programming.  If you aren't familiar with socket programming (I'm willing to bet most people are not), please stop reading and complete [this tutorial](https://ruslanspivak.com/lsbaws-part1/). 

To begin with, David starts with this code:

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
        req = client.recv(100)  #keeps checking for data that sent by the client on the connection.
        if not req: break
        result = fib(int(req))
        resp = str(result).encode('ascii') + b'\n'
        client.send(resp) # sends data back to the client.
    print("Closed")
    
fib_server(('', 25000))
```
