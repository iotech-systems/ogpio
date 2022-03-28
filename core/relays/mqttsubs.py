#!/usr/bin/env python3

"""
   mqttops only writes to command file in cmds folder
"""

import os, time
import xml.etree.ElementTree as et
import paho.mqtt.client as mqtt
from core.mqtt.topics import topics
from core.utils import utils
from core.channelcmd import channelCMD


class mqttSubs(object):

   def __init__(self, elmt: et.Element):
      self.xml = elmt
      self.brokerip: str = ""
      self.brokeruid: str = ""
      self.brokerpwd: str = ""
      self.edge_hostname: str = ""
      self.mqtt: mqtt.Client = \
         mqtt.Client(client_id="CLT_ID_00", clean_session=True,
            userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
      self.mqtt.on_message = self.on_message
      self.mqtt.on_connect = self.on_connect
      self.mqtt.on_connect_fail = self.on_conn_error
      self.mqtt.on_subscribe = self.on_subscribe
      self.__ip_uid_pwd__()

   def init(self):
      self.connect()
      self.subscribe_topics()

   def connect(self):
      self.mqtt.user_data_set(self)
      self.mqtt.connect(host=self.brokerip, port=1883)

   def on_connect(self, clt, udata, msg, rc):
      if rc == 0:
         print(f"\n\t-- mqtt_clt on_connect ok --\nudata: {udata}\n")
         udata: mqttSubs = udata
         udata.subscribe_topics()
         # -- read topics without callback --
         clt: mqtt.Client = clt
         clt.loop_start()
      else:
         print("\n\t---\n\tmqtt_clt unable to connect\n\t---\n")
         exit(1)

   def subscribe_topics(self):
      _topics = topics.system_topics(self.xml)
      print("_topics")
      print(_topics)
      self.mqtt.subscribe(_topics)

   """
      on_subscribe(client, userdata, mid, granted_qos)
   """
   def on_subscribe(self, clt, udata, mid, qos):
      print("on_subscribe")
      print(qos)

   def on_message(self, clt, udata, msg):
      print("on_message")
      msg: mqtt.MQTTMessage = msg
      print(f"topic:  {msg.topic}")
      print(f"payload: {msg.payload}")
      if msg.topic.endswith("/cmd"):
         channel_id = self.__channel_id__(msg)
         channelCMD.save_cmd(channel_id, msg.payload)

   def run(self):
      self.mqtt.loop_start()

   def on_conn_error(self, clt, udata, msg):
      print([clt, udata, msg])

   def __ip_uid_pwd__(self):
      self.brokerip = self.xml.attrib["ip"]
      self.brokeruid = self.xml.attrib["uid"]
      self.brokerpwd = self.xml.attrib["pwd"]

   def __channel_id__(self, msg: mqtt.MQTTMessage) -> [False, int]:
      arr = msg.topic.split("/")
      if arr[3] == "channels":
         return int(arr[4])
      else:
         return False
