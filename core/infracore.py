

import queue


class infraCore(object):

   def __init__(self, mqttQ: queue.SimpleQueue):
      self.mqttQ = mqttQ

   def mqttq_pub(self, obj):
      assert self.mqttQ is not None
      self.mqttQ.put(obj)
