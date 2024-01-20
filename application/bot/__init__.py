import threading
import logging
import time

bot_logger = logging.getLogger('bot')

__all__ = ['bots', 'bot_logger']

class fixedIntervalThread:
  def __init__(self, work, interval, args=()):
    self.work=work
    self.flag=False
    self.interval = interval
    self.args = args
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

  def doing(self):
    while True:
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
