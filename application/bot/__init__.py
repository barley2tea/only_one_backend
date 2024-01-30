import threading
import logging
import time
import datetime

bot_logger = logging.getLogger('bot')

__all__ = ['bots', 'bot_logger']

class fixedIntervalThread:
  def __init__(self, work, interval, args=(), active_times=None):
    self.work=work
    self.flag=False
    self.interval = interval
    self.args = args
    self.active_times = active_times
    self.thread = threading.Thread(target=self.doing)

  def is_alive(self):
    return self.thread.is_alive()
  def start(self):
    self.thread.start()
  def stop(self):
    self.set()

  def set(self):
    self.flag = True
  def reset(self):
    self.flag = False
  def run(self):
    self.work(*self.args)

  def is_active_time(self, t=None):
    if self.active_times is None: return True
    if t is None: t = datetime.datetime.now().time()
    for tm in active_times:
      if tm[0] <= t <= tm[1]:
        return True
    return False

  def doing(self):
    while True:
      if self.is_active_time():
        self.run()
      time.sleep(self.interval)
      if self.flag:
        self.reset()
        break

class _bots:
  def __init__(self):
    self.items = {}
  def __setitem__(self, key, val):
    self.items[key] = val
  def __getitem__(self, key):
    return self.items[key]

  def all_start(self):
    for k in self.items.keys():
      if not self.items[k].is_alive():
        self.items[k].start()

  def all_stop(self):
    for k in self.items.keys():
      if self.items[k].is_alive():
        self.items[k].stop()


bots = _bots()
