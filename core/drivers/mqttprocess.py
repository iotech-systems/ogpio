
import setproctitle
import multiprocessing
import queue, typing as t
from core.strucs import *
from core.mqtt.mqttmonitor import mqttMonitor
from core.gpio.modbus.modbus_driver import modbusDriver
from core.gpio.internal.internal_driver import internalDriver
from core.hostgpioxml import hostGpioXml
from core.strucs import driverTypes
from core.mqtt.topics import topics


hostgpio = hostGpioXml()
# -- gpio drivers --
MQTT_DRIVERS: t.List[et.Element] = hostgpio.drivers(driverTypes.MQTT)
if len(MQTT_DRIVERS) == 0:
   print("MQTT_DRIVERS_NOT_FOUND")


class mqttProcess(multiprocessing.Process):

   RUNNING_DRIVER = []
   MQTT_PUB_QUEUE: [None, queue.SimpleQueue] = None
   ETC_HOSTNAME: str = None

   @staticmethod
   def start_all():
      # -- --
      def init_start_driver(drvr: et.Element):
         tmpMqttProcess: mqttProcess = mqttProcess(drvr, mqttProcess.MQTT_PUB_QUEUE)
         tmpMqttProcess.start_mqtt_monitor()
         mqttProcess.RUNNING_DRIVER.append(tmpMqttProcess)
         # -- start mqtt driver process --
         tmpMqttProcess.start()
      # -- on each driver --
      for driver in MQTT_DRIVERS:
         init_start_driver(driver)
      # -- --

   def __init__(self, driver: et.Element, mqtt_pub_que: queue.SimpleQueue):
      super().__init__()
      self.drvr_xml: et.Element = driver
      self.drvr_id = self.drvr_xml.attrib["id"]
      self.name = f"MQTT_PROCESS_{self.drvr_id}"
      self.mqtt_pub_que = mqtt_pub_que
      self.mqtt_info: [None, mqttInfo] = None
      self.mqtt_monitor: [None, mqttMonitor] = None
      self.buses: [None, t.List[et.Element]] = None

   def start_mqtt_monitor(self) -> bool:
      try:
         _topics = topics.create_pin_topic_list(self.drvr_xml, mqttProcess.ETC_HOSTNAME)
         self.mqtt_monitor = mqttMonitor(self.drvr_xml)
         self.mqtt_monitor.set_topics(_topics)
         self.mqtt_monitor.connect()
         # -- it will run as non-blocking thread --
         self.mqtt_monitor.loop(mqttLoops.START)
         while not self.mqtt_monitor.mqtt_clt_connected:
            time.sleep(0.2)
         # -- subscribe topics --
         self.mqtt_monitor.subscribe()
         return True
      except Exception as e:
         print(e)
         return False

   def run(self) -> None:
      # -- start mqtt monitor --
      setproctitle.setproctitle("ogpio-mqtt-mon")
      self.__start_bus_drivers__()
      while True:
         self.__loop__()
         time.sleep(4.0)

   def __loop__(self):
      print(f"\n\t[ __process_loop__: {self.name} ]\n")

   def __start_bus_drivers__(self):
      self.buses = self.drvr_xml.findall("bus")
      if len(self.buses) == 0:
         print("[ no buses found ]")
         return
      # -- get buses found --
      bus_types = []
      for b in self.buses:
         _type = b.attrib["type"]
         if _type in bus_types:
            continue
         bus_types.append(_type)
      # -- start per bus type --
      for bus_type in bus_types:
         self.__on_bus_type__(bus_type)

   def __on_bus_type__(self, bus_type: str):
      try:
         _btype = bus_type.upper()
         if _btype == busTypes.MODBUS:
            modbusDriver.init_start(mqttProcess.MQTT_PUB_QUEUE)
         elif _btype == busTypes.INTERNAL:
            internalDriver.init_start(mqttProcess.MQTT_PUB_QUEUE)
         else:
            pass
      except Exception as e:
         print(e)

   def __set_mqtt_info__(self):
      ap: argsParser = argsParser(self.drvr_xml)
      ip = ap.get_item("ip")
      port = ap.get_item("port")
      uid = ap.get_item("uid")
      pwd = ap.get_item("pwd")
      self.mqtt_info = mqttInfo(ip, port, pwd, uid)
