
import minimalmodbus as mm
import typing as t, time, queue
import xml.etree.ElementTree as et
from core.utils import utils
from core.xmlutils import xmlUtils
from core.gpio.busdriver import busDriver
from core.gpio.gpioUtils import gpioUtils
from core.gpio.pincmd import pinCMD
from core.strucs import \
   argsParser, busTypes, serialInfo, pinStateEvent, mqttInfo
from core.gpio.modbus.modbus_instrument import modbusInstrument
from core.gpio.modbus.modbus_node import modbusNode
from core.gpio.pincmdfile import pinCmdFileOps
from core.gpio.pinruntime import pinRuntime


class modbusDriver(busDriver):

   __instance__: [None, object] = None

   @staticmethod
   def init_start(mqtt_que: queue.SimpleQueue) -> bool:
      try:
         if modbusDriver.__instance__ is not None:
            return True
         modbusDriver.__instance__ = modbusDriver(mqtt_que)
         modbusDriver.__instance__.start()
         return True
      except Exception as e:
         print(e)
         return False

   def __init__(self, mqtt_que: queue.SimpleQueue):
      super().__init__(busTypes.MODBUS, mqtt_que)

   def run(self) -> None:
      # -- init code --
      if not self.__init_bus_node_pins__():
         raise Exception("ErrorOnInitBusNodePins")
      # -- end of init --
      while True:
         try:
            print("\t -- [ modbus_driver.run ] --")
            dts_ms = self.epoch_ms()
            self.print_info()
            self.__loop__()
            loop_sleep = self.loop_delay_secs(dts_ms)
            time.sleep(loop_sleep)
         except Exception as e:
            print(e)
            time.sleep(4.0)

   def __loop__(self):
      for bus in self.driver_buses:
         if not xmlUtils.is_bus_of_type(bus, self.bustype.upper()):
            continue
         self.__on_each_bus__(bus)
      # -- end loop --

   """
      cmd file hold pin number to be used
   """
   def __process_bus_node_cmds__(self, bus_ap: argsParser
         , node_ap: argsParser, bnode_pins: t.List[et.Element]):
      # -- --
      bus_address = int(bus_ap.get_item("id"))
      node_address = int(node_ap.get_item("address"))
      node_settings = node_ap.get_item("settings")
      sinfo: serialInfo = serialInfo(node_settings)
      ttydev = utils.ttyusb(bus_ap)
      # -- modbus instrument --
      mbinst: modbusInstrument = modbusInstrument(None, ttydev, node_address, mm.MODE_RTU)
      # -- --
      for bn_pin in bnode_pins:
         pin = int(bn_pin.attrib["id"])
         # -- full pin address  --
         FULL_PIN_ADDRESS = gpioUtils.full_pin_address(bustype=busTypes.MODBUS
            , busid=bus_address, nodeid=node_address, pinid=pin)
         # -- build cmd file name --
         cmd_file_name = gpioUtils.cmd_file_name(FULL_PIN_ADDRESS)
         cmd_file_buff = pinCmdFileOps.read(cmd_file_name)
         if cmd_file_buff is False:
            print(f"[ NO_CMD_FILE -> modbus: {bus_address}; node: {node_address}; pin: {pin}; ]")
            continue
         # -- --
         temp = bn_pin.attrib["inverted"]
         pc: pinCMD = pinCMD(FULL_PIN_ADDRESS, cmd_file_buff, temp)
         if not pc.compute_pinval():
            pass
         # -- set & confirm pin --
         print(f"\t ->bus: modbus; node: {node_address}; reg/pin: {pin}; val: {pc.pinval}")
         mbinst.set_serial_info(sinfo)
         pinval = int(pc.pinval)
         if self.__write_confirm_pin__(mbinst, pin, pinval):
            pinRuntime.update_pin(pc.pinadr, pc.actcmd, pc.toggle, pc.pinval_str)
            """mqtt_info: mqttInfo = mqttInfo()
            pin_state_event: pinStateEvent = \
               pinStateEvent(mqtt_info, self.bustype, bus_address, node_address, pin, pinval)
            self.insert_into_mqtt_que(pin_state_event)"""

   def __write_confirm_pin__(self, mbinst: modbusInstrument, pin: int, pinval: int) -> bool:
      try:
         mbinst.write_bit(pin, pinval)
         # self.__read_pin__(mbinst, pin)
         return True
      except Exception as e:
         print(e)
         return False

   def __init_bus_node_pins__(self) -> bool:
      print("__init_bus_node_pins__")
      # -- --
      buses = []
      for b in self.driver_buses:
         if not xmlUtils.is_bus_of_type(b, self.bustype.upper()):
            continue
         buses.append(b)
      # -- --
      def on_bus(bus):
         bus_args: argsParser = argsParser(bus)
         for node in bus.findall("node"):
            mbnode: modbusNode = modbusNode(node, bus_args)
            mbnode.init_pins()
      # -- on each bus --
      for _bus in buses:
         on_bus(_bus)
      # -- return --
      return True
