#!/usr/bin/env python3

"""
   mqttops only writes to command file in cmds folder
"""
import paho.mqtt.client as mqtt
from core.gpio.gpioUtils import gpioUtils
from core.gpio.pincmdfile import pinCmdFileOps
from core.strucs import *


class mqttMonitor(object):

   @staticmethod
   def gen_monitor_id(elm: et.Element) -> str:
      ap: argsParser = argsParser(elm)
      return "KEY_%s_%s" % (ap.dictionary["ip"], ap.dictionary["port"])

   def __init__(self, drvr: et.Element):
      self.xml: et.Element = drvr
      self.cltid = self.xml.attrib["id"]
      self.drvr_args: argsParser = argsParser(self.xml)
      self.broker_ip: str = self.drvr_args.dictionary["ip"]
      self.broker_port: int = int(self.drvr_args.dictionary["port"])
      self.broker_uid: str = self.drvr_args.dictionary["uid"]
      self.broker_pwd: str = self.drvr_args.dictionary["pwd"]
      self.edge_hostname: str = ""
      # -- topics --
      self.gpio_topics: [] = [None, []]
      # -- mqtt_clt client --
      self.mqtt_clt_connected: bool = False
      self.mqtt_clt: mqtt.Client = \
         mqtt.Client(client_id=self.cltid, clean_session=False
            , userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
      # -- callbacks --
      self.mqtt_clt.on_message = self.__on_message__
      self.mqtt_clt.on_connect = self.__on_connect__
      self.mqtt_clt.on_connect_fail = self.__on_conn_fail__
      self.mqtt_clt.on_subscribe = self.__on_subscribe__

   def connect(self):
      print("-- mqtt_clt connecting --")
      self.mqtt_clt.user_data_set(self)
      rval: int = self.mqtt_clt.connect(host=self.broker_ip, port=self.broker_port)
      print(f"\tconnect rval: {rval}")

   def subscribe(self):
      print(f"\n-- subscribe_topics --")
      for t in self.gpio_topics:
         print(f"\tsubscribing: {t[0]}")
         self.mqtt_clt.user_data_set(t)
         self.mqtt_clt.subscribe(t)
         time.sleep(0.1)
      # -- send to broker --

   def set_topics(self, _topics: []):
      self.gpio_topics = _topics

   def loop(self, looptype: str = mqttLoops.FOREVER):
      if looptype == mqttLoops.FOREVER:
         self.mqtt_clt.loop_forever()
      elif looptype == mqttLoops.START:
         self.mqtt_clt.loop_start()
      else:
         pass

   """ - - - - - - - - - - - - - - - - - - - - - - - - 
      callbacks 
   - - - - - - - - - - - - - - - - - - - - - - - - """

   def __on_connect__(self, clt, udata, msg, rc):
      print(f"__on_connect__: {udata}")
      if rc == 0:
         mqttmon: mqttMonitor = udata
         mqttmon.mqtt_clt_connected = True
      else:
         pass

   def __on_message__(self, clt, udata, msg: mqtt.MQTTMessage):
      print("\non_message\n")
      msg: mqtt.MQTTMessage = msg
      print(f"topic:  {msg.topic}; payload: {msg.payload}")
      PIN_LBL = gpioUtils.full_pin_address(topic=msg.topic)
      cmd_file_name = gpioUtils.cmd_file_name(PIN_LBL)
      if pinCmdFileOps.write(cmd_file_name, msg.payload):
         print(f"cmd file saved: {cmd_file_name}")
      else:
         print(f"cmd file NOT saved: {cmd_file_name}")

   def __on_subscribe__(self, clt, udata, mid, qos):
      print(f"\t + subscribed: {mid} - {udata[0]}")

   def __on_conn_fail__(self, clt, udata, msg):
      print([clt, udata, msg])
