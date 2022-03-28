import time
import typing as t
import xml.etree.ElementTree as et
from queue import SimpleQueue
from core.mqtt.mqttpubbot import mqttPubBot
from core.mqtt.mqttmonitor import mqttMonitor
from core.mqtt.topics import topics
import core.machine as mach


class mqttStarter(object):

   MQTT_MONITORS: {} = {}
   MQTT_TOPICS: {} = {}

   def __init__(self):
      self.mqtt_queue: [None, SimpleQueue] = None
      self.mqttpub: [None, mqttPubBot] = None

   def start_publisher(self, SQ: SimpleQueue) -> bool:
      try:
         print("\n\t-- starting mqttpubbot --\n")
         self.mqttpub = mqttPubBot(SQ)
         self.mqttpub.start()
         return True
      except Exception as e:
         print(e)
         return False

   def start_monitor(self, _GPIO_DRIVERS: t.List[et.Element]) -> bool:
      # -- on each gpio driver; do topics --
      self.__load_pin_topics__(_GPIO_DRIVERS)
      # -- on each gpio driver; do monitors --
      self.__start_monitors__(_GPIO_DRIVERS)
      # -- subscribe all topics --
      return True

   def __create_monitor__(self, _driver: et.Element, _mon_id):
      try:
         # -- init monitor & start --
         mqttmon: mqttMonitor = mqttMonitor(_driver, _mon_id)
         self.MQTT_MONITORS[_mon_id] = mqttmon
         arr = mqttStarter.MQTT_TOPICS[_mon_id]
         mqttmon.set_topics(arr)
         mqttmon.connect()
         mqttmon.loop("START")
         while not mqttmon.mqtt_clt_connected:
            time.sleep(0.1)
         mqttmon.subscribe()
      except Exception as e:
         print(e)

   def __start_monitors__(self, _GPIO_DRIVERS):
      for _driver in _GPIO_DRIVERS:
         _mon_id = mqttMonitor.gen_monitor_id(_driver)
         if _mon_id not in self.MQTT_MONITORS:
            self.__create_monitor__(_driver, _mon_id)

   def __load_pin_topics__(self, _GPIO_DRIVERS):
      # -- per driver --
      def __per_driver__(_driver):
         _mon_id = mqttMonitor.gen_monitor_id(_driver)
         if _mon_id not in mqttStarter.MQTT_TOPICS:
            mqttStarter.MQTT_TOPICS[_mon_id] = []
         _topics = topics.create_pin_topic_list(_driver, mach.ETC_HOSTNAME)
         mqttStarter.MQTT_TOPICS[_mon_id].extend(_topics)
      # -- iterate ---
      for _driver in _GPIO_DRIVERS:
        __per_driver__(_driver)
