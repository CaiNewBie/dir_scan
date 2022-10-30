# coding=utf-8
import os
from queue import Queue
from config import *
import threading
import requests
from fake_useragent import UserAgent
import sys


class Dir_scan(object):
    def __init__(self, url, dict, thread_count):
        self._url = url
        self._dict = dict
        self._queue = Queue()
        self._thread_count = thread_count
        self._threads = []
        self._total_count = 0

    def _init(self):
        if not os.path.exists(dict_base_path + self._dict):
            print("字典不存在！")
            sys.exit(-1)
        with open(dict_base_path + self._dict, "r") as f:
            for d in f:
                temp_d = self._check_dict(d)
                if "://" in self._url:
                    self._queue.put(self._url + "/" + temp_d)
                else:
                    self._queue.put("http://" + self._url + "/" + temp_d)
                    self._queue.put("https://" + self._url + "/" + temp_d)
            self._total_count = self._queue.qsize()

    def _check_dict(self, path):
        return path.lstrip("/")

    def start(self):
        self._init()
        for i in range(self._thread_count):
            self._threads.append(self.Dir_scan_run(self._queue, self._total_count))
        for t in self._threads:
            t.start()
        for t in self._threads:
            t.join()

    class Dir_scan_run(threading.Thread):
        def __init__(self, queue, total_count):
            super().__init__()
            self._queue = queue
            self._ua = UserAgent()
            self._total_count = total_count

        def run(self):
            while not self._queue.empty():
                scan_url = self._queue.get()
                self._msg(self._queue.qsize())
                headers = {
                    "User-Agent": self._ua.random
                }
                try:
                    response = requests.get(scan_url.rstrip(), headers=headers)
                    if response.status_code == 200:
                        print(f"\n[*]{scan_url.rstrip()}")
                except Exception as e:
                    pass

        def _msg(self, last_count):
            last = round((last_count / self._total_count) * 100, 2)
            already_do = round(100 - last, 2)
            sys.stdout.write(f"\r已跑:{already_do}%,剩余:{last}%")


url = input("请输入网址:")
dict = "php2.txt"

scan = Dir_scan(url, dict, 10)
scan.start()
