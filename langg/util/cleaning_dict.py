from __future__ import annotations

import time
import threading
import logging

from datetime import (datetime, date)
from typing import Dict
from collections.abc import MutableMapping

LOG: logging.Logger = logging.getLogger('langg')


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class LastTouched:
    def __init__(self, o: object):
        self.touched: date = None
        self.o: object = o
        self.touch()

    def touch(self):
        self.touched = datetime.now()


FIVE_MINUTE_S: int = 300


class TimingDict(MutableMapping):

    def __init__(self, interval: int = FIVE_MINUTE_S, *args, **kwargs):
        self.lock = threading.Lock()
        self.store: Dict[int, LastTouched] = dict()
        self.update(dict(*args, **kwargs))
        self.timer = RepeatTimer(interval, self._clean)
        self.timer.start()

    def _clean(self):
        now: date = datetime.now()
        with self.lock:
            for k in list(self.store.keys()):
                LOG.debug(
                    f'Cleaning {{key: {k}, time: {self.store[k].touched}}}')
                if self.store[k].touched < now:
                    del self.store[k]

    def __getitem__(self, key):
        with self.lock:
            lt: LastTouched = self.store[key]
            lt.touch()
            return lt.o

    def __setitem__(self, k, v):
        with self.lock:
            self.store[k] = LastTouched(v)

    def __delitem__(self, key):
        with self.lock:
            del self.store[key]

    # This is questionable
    def __iter__(self):
        with self.lock:
            return iter(self.store)

    def __len__(self):
        return len(self.store)


if __name__ == '__main__':
    d = TimingDict(interval=2)
    d['k1'] = 'v1'
    d['k2'] = 'v2'
    for k, v in d.items():
        print(k, v)
    time.sleep(2)
    d['k3'] = 'v3'
    for k, v in d.items():
        print(k, v)
    d.timer.cancel()
