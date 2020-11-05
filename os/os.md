# OS Interview Questions

## What is a process and process table?

A process is a running program. The program itself is a lifeless thing, it’s just a bunch of instructions, sitting on the disk, waiting to spring into action. It’s the operating system that takes these bytes and gets them running.

A process table (or a process list) is a data structure to keep track of all the running programs in the system. It’s a list of PCB (Process Control Block), which is a structure that contains information about a process.

## What are different states of process?

There are three different states a process can be in at a given time.
- Running. A process is running on a processor. It is executing instructions.
- Ready. A process is ready to run but the OS has chosen not to run it at this given moment.
- Blocked. A process has performed some kind of operation that makes it not ready to run until some other event takes place. For example, when a process initiates an I/O request to a disk, it becomes blocked and thus some other process can use the processor.

## What is a thread? What are the differences between process and thread?

A thread is an abstraction for a single running process. Each thread is very much like a separate process. Unlike processes, threads share the same address space and thus can access the same data.

Like processes, each thread has its own private set of registers it uses for computation. Like processes, when switching from running a thread to running the other, a context switch must take place. With process we save state to a process control block (PCB); we need one or more thread control blocks (TCBs) to store the state of each thread of a process.

A difference between processes and threads is in the context switch we perform between threads as compared to processes: the address space remains the same (i.e., there is no need to switch which page table we are using). Another difference between threads and processes concerns the stack. In a simple model of the address space of a classic process (i.e. single-threaded process), there is a single stack. However, in a multithreaded process, each thread runs independently and of course may call into various routines to do whatever work it is doing; as a result, there will be one stack per thread.

Why use threads? First, parallelism. Imagine you are writing a program that performs operations on very large arrayings, for example, incrementing the value of each element in the array by some amount. With multiple processors, you have the potential of speeding up this process considerably by using the processors to each perform a portion of the work. Using a thread per CPU to do this work is a natural and typical way to make programs run faster on modern hardware.

Second, to avoid blocking program progress due to slow I/O. Imagine that you are writing a program that performs I/O. Instead of waiting, your program may wish to do something else, including utilizing the CPU to perform computation. Using threads is a natural way to avoid getting stuck; while one thread in your program waits (i.e., is blocked waiting for I/O), the CPU scheduler can switch to other threads, which are ready to run and do something useful. Threading enables overlap of I/O with other activities within a single program, much like multiprogramming did for processes across programs.

## What is multiprogramming? How does multiprogramming differ from multithreading?
Instead of just running one job at a time, in multiprogramming the OS would load a number of jobs into memory and switch them rapidly, thus improving CPU utilization.

## What is a page table?
A page table is a per-process data structure that records the placement of each virtual page of the address space in physical memory. That is, the major role of the page table is to store address translations for each of the virtual pages of the address space to its physical memory location.

## What is a page fault?
Using swapping, a page table entry for a virtual memory address may be present in the page table, but the page itself is not present in main memory. This is indicated by a present bit of 0. This act of accessing a page that is not in physical memory is commonly referred to as a page fault.

## What are the different scheduling metrics?
- Turnaround time. t_turnaround = t_completion - t_arrival
- Response time. t_response = t_first_run - t_arrival

## What are the different scheduling algorithms?
First In, First Out (FIFO) / First Come, First Served (FCFS). The first job to arrive gets run first. If earlier jobs are run for long periods of time, then the convoy effect arises (i.e., a number of relatively-short potential consumers get queued behind a heavyweight resource consumer).

Shortest Job First (SJF). It runs the shortest job first, then the next shortest, and so on. If all processes arrive at the same time, SJF is indeed an optimal scheduling algorithm. However, even if the relatively-short jobs arrive shortly after a heavyweight one, they are still forced to wait until the heavyweight has completed;and thus suffer the same convoy problem.

Shortest-Time-to-Completion (STCF). This scheduler adds preemption to SJF. Any time a new job enters the system, the STCF scheduler determines which of the remaining jobs (including the new job) has the least time left, and schedules that one. While great for turnaround time, this approach is quite bad for response time and interactivity. Imagine sitting at a terminal, typing, and having to wait 10 seconds to see a response from the system just because some other job got scheduled in front of yours: not too pleasant.

Round Robin (RR). Instead of running jobs to completion, RR runs a job for a time slice and then switches to the next job in the run queue. RR, with a reasonable time slice, is an excellent scheduler; but the turnaround time is pretty awful.

Multi-level Feedback Queue (MLFQ). MLFQ has a number of distinct queues, each assigned a different priority level. At any given time, a job (or more) is ready to run. A job with higher priority is chosen to run. In the case where multiple jobs have the same priority, we use RR among these jobs. When a job enters the system, it is placed at the highest priority. Once a job uses up its time allotment at a given level, its priority is reduced. After some time period S, move all jobs in the system to the topmost queue. By performing these steps, MLFQ tries to optimize turnaround time and minimize response time.

## What is a race condition? How to avoid it?
A race condition arises if multiple threads of execution enter the critical section at roughly the same time; both attempt to update the shared data structure, leading to a surprising (and perhaps undesirable) outcome.

For example, you have two threads attempting to increment a counter (which is a shared resource). Suppose counter = 50. Thread A is executing the add statement, and before thread A stores 51 back to counter, context switch happens. Thread B then uses the old value of counter (where instead it should have used the new value) and executes with up to the add statement, and context switch happens. When A completes the remaining code, and context switch occurs again, thread B completes its execution and writes 51 to counter, where instead the final value should be 52.

Because multiple threads executing this code can result in a race condition, we call this code a critical section. A critical section is a piece of code that accesses a shared variable and must not be concurrently executed by more than one thread.

What we really want for this code is mutual exclusion. This property guarantees that if one thread is executing within the critical section, the others will be prevented from doing so.

One way to solve this problem would be to have more powerful instructions that, in a single step, did exactly whatever we needed done and thus removed the possibility of untimely interrupt. For example, what if we had a super instruction that looked like this: memory-add 0x8049a1c, $0x1. This instruction executes atomically. But in the general case, we won’t have such an instruction, at least in a sane instruction set.

Thus, we will instead ask the hardware for a few useful instructions upon which we can build a general set of synchronization primitives. One of them is called locks. Locks are useful to protect critical sections.

```
pthread_mutex_t lock;
pthread_mutex_lock(&lock);
x = x + 1;
pthread_mutex_unlock(&lock);
```

One of the implements of lock() and unlock() is by using TestAndSet().

```
int TestAndSet(int* old_ptr; int new) {
    int old = *old_ptr;
    *old_ptr = new;
    return old;
}

typedef struct __lock_t {
    int flag;
} lock_t;

void init(lock_t *lock) {
    lock->flag = 0;
}

void lock(lock_t *lock) {
    while (TestAndSet(&lock->flag, 1) == 1) 
; // spin-wait
}

void unlock(lock_t *lock) {
    lock->flag = 0;
}
```

Another primitive is called semaphore, which was invented as a single primitive for all things related to synchronization. A semaphore is an object with an integer value that we can manipulate with two routines: sem_wait() and sem_post().

```
#include <semaphore.h>
sem_t s;
sem_init (&s, 0, 1); // 0: used by the same process, 1: init value for s
```

We can use semaphores as locks. That is, we use binary semaphores (initialized value = 0).

We implement semaphores using locks and condition variables.

```
typedef struct __sem_t {
    int value;
    pthread_cond_t cond;
    pthread_mutex_t lock;
} sem_t;

void sem_init(sem_t *s, int value) {
    s->value = value;
    cond_init(&s->cond);
    mutex_init(&s->lock);
}

void sem_wait(sem_t *s) {
    mutex_lock(&s->lock);
    while (s->value <= 0) {
        cond_wait(&s->cond, &s->lock);
    }
    s->value--;
    mutex_unlock(&s->lock);
}

void sem_post(sem_t *s) {
    mutex_lock(&s->lock);
    s->value++;
    cond_signal(&s->cond);
    mutex_unlock(&s->lock);
}
```

What is a deadlock? How to avoid/recover from a deadlock?
A deadlock occurs when two threads each lock a different variable at the same time and then try to lock the variable that the other thread already locked. As a result, each thread stops executing and waits for the other thread to release the variable. Because each thread is holding the variable that the other thread wants, nothing occurs, and the threads remain deadlocked.

In order for a deadlock to occur, you must have all four of the following conditions met:
- Mutual Exclusion: Only one process can access a resource at a given time.
- Hold and Wait: Processes already holding a resource can request additional resources, without relinquishing their current resources.
- No Preemption: One process cannot forcibly remove another process' resource.
- Circular Wait: Two or more processes form a circular chain where each process is waiting on another resource in the chain.

Deadlock prevention entails removing any of the above conditions, but it gets tricky because many of these conditions are difficult to satisfy. For instance, removing #1 is difficult because many resources can only be used by one process at a time (e.g., printers). Most deadlock prevention algorithms focus on avoiding condition #4: circular wait.
