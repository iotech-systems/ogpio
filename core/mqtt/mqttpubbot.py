
import threading, queue, uuid
import paho.mqtt.client as mqtt
from core.mqtt.topics import topics
from core.strucs import *
import core.machine as mach


class mqttPubBot(threading.Thread):

   def __init__(self, q: queue.SimpleQueue):
      super().__init__()
      self.mqttpub_queue: queue.SimpleQueue = q
      self.mqtt_clts = {}

   def run(self) -> None:
      while True:
         try:
            print("-- mqttPubBot::run --")
            obj = self.mqttpub_queue.get(timeout=4.0)
            if obj is None:
               continue
            if isinstance(obj, channelPinStateEvent):
               obj: channelPinStateEvent = obj
               self.__pub_pin_state_event__(obj)
         except queue.Empty:
            print("mqttPubBot::EmptyQueue")
         except Exception as e:
            print(e)

   def __pub_pin_state_event__(self, obj: channelPinStateEvent):
      # -- on_pub: on_publish(client, userdata, mid) --
      guid = uuid.uuid1().hex
      def on_pub(clt, udata, mid):
         nonlocal guid
         if udata == guid:
            print(f"\tpublish ok: {guid}")
      # -- end on_pub --
      host = mach.ETC_HOSTNAME
      topic = topics.pub_topic_channel_pin_event(host
         , obj.channel_id, obj.pin_id, obj.pin_event)
      print(f"\tpushing -> topic: {topic}; + val: {obj.val};")
      mqtt_clt: mqtt.Client = self.__get_mqttclt__(obj.mqttinfo)
      mqtt_clt.user_data_set(guid)
      mqtt_clt.on_publish = on_pub
      # -- push to broker --
      mqtt_clt.publish(topic=topic, payload=obj.val)

   def __get_mqttclt__(self, mqttI: mqttInfo) -> mqtt.Client:
      XARR = [None, ""]
      # -- if not found -> make new --
      if mqttI.host not in self.mqtt_clts.keys():
         tmp: mqtt.Client = mqtt.Client(client_id=f"{mqttI.host}")
         if mqttI.pwd not in XARR and mqttI.uid not in XARR:
            tmp.connect(host=mqttI.host)
         else:
            tmp.connect(host=mqttI.host)
         self.mqtt_clts[mqttI.host] = tmp
         time.sleep(1.0)
      # -- return mqtt_clt clt --
      clt: mqtt.Client = self.mqtt_clts[mqttI.host]
      if not clt.is_connected():
         clt.reconnect()
      return clt
