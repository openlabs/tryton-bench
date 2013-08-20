#!/bin/env python
# -*- coding: utf-8 -*-
"""
    tryton_bench

    Stress test the server with several concurrent requests

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: Modified BSD, see LICENSE for more details.
"""


import argparse
import time
import operator
from multiprocessing import Process
from multiprocessing import Queue

from tryton_rpc import HttpClient


class Scenario:
    def __init__(self, module_name):
        self.module = __import__(module_name)

    def model(self):
        return self.module.MODEL

    def method(self):
        return self.module.METHOD

    def generate(self):
        return self.module.generate()


class Timer(object):
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        self.finish = time.time()

    def duration(self):
        return self.finish - self.start


class Lap:
    def __init__(self):
        self.data = [time.time()]

    def note(self):
        self.data.append(time.time())

    def last(self):
        return self.data[-1] - self.data[-2]

    def elapsed(self):
        return self.data[-1] - self.data[0]


def timeit(func):
    timer = Timer()

    def f(*args, **kwargs):
        with timer:
            result = func(*args, **kwargs)
        duration = timer.duration()
        return (result, duration)

    return f


def blast_server(env, scenario_name, num, queue, completed):
    INTERVAL = num // 10
    scenario = Scenario(scenario_name)
    client = HttpClient(env.url, env.database, env.user, env.password)
    good, bad = 0, 0
    for i in range(num):
        data = scenario.generate()
        status_code = client.call(scenario.model(), scenario.method(),
                *data.get('args', []), **data.get('kwargs', {}))
        if status_code >= 400 and status_code < 600:
            bad += 1
        else:
            good += 1
        if i % INTERVAL == 0:
            queue.put(INTERVAL)
    queue.put(num % INTERVAL)
    completed.put((num, good, bad))
    return num


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='localhost',
            help='URL of the JSON RPC server')
    parser.add_argument('-d', '--database', required=True,
            help='Tryton database')
    parser.add_argument('-u', '--user', required=True, help='Tryton user')
    parser.add_argument('-p', '--password', required=True,
            help='Tryton password')
    parser.add_argument('-r', '--requests', type=int, required=True,
            help='Number of requests')
    parser.add_argument('-c', '--connections', type=int, required=True,
            help='Number of concurrent connections')
    parser.add_argument('-s', '--scenario', required=True,
            help='Module which will generate test cases')
    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    print "TrytonBench: Stress test JSON RPC Server"
    print "----------------------------------------\n"
    print "  Target                 :  {url}/{db}".format(
            url=args.url, db=args.database)
    print "  Requests to serve      :  {}".format(args.requests)
    print "  Concurrent connections :  {}".format(args.connections)
    print "\n"

    chunk_size = args.requests // args.connections
    pool = []
    progress, completed = Queue(), Queue(args.connections)

    lap = Lap()
    for i in range(args.connections):
        #sender, receiver = Pipe()
        #print receiver
        if i == args.connections - 1:
            chunk_size = args.requests - (chunk_size * i)
        p = Process(target=blast_server,
                args=(args, args.scenario, chunk_size, progress, completed))
        pool.append(p)
        p.start()

    total = 0
    last_percentage, percentage = 0, 0
    print "  Percentage of requests served - "
    while not completed.full():
        total += progress.get()
        percentage = int(float(100 * total) / args.requests)
        if percentage - last_percentage >= 10:
            last_percentage = percentage
            lap.note()
            print "   {:{w1}d}%  ---  {:0.2f} seconds".format(
                    percentage, lap.elapsed(), w1=4)

    aggregate = [0, 0, 0]  # [num, good, bad]
    for i in range(args.connections):
        pool[i].join()
        aggregate = map(operator.add, aggregate, completed.get())

    print "\n"
    print "  Successful requests    :  {}".format(aggregate[1])
    print "  Failed requests        :  {}".format(aggregate[2])
    print "  Total time taken       :  {:0.2f} seconds".format(lap.elapsed())


if __name__ == '__main__':
    main()
