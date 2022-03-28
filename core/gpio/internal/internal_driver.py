
import typing as t, time, queue
import xml.etree.ElementTree as et
from core.gpio.busdriver import busDriver
from core.gpio.gpioUtils import gpioUtils
from core.gpio.pincmd import pinCMD
from core.strucs import argsParser, busTypes
from core.xmlutils import xmlUtils
from core.gpio.bus.busnode import busNode
from core.gpio.internal.internal_node import internalNode
from core.gpio.anygpio import gpio
from core.gpio.pinruntime import pinRuntime
from core.gpio.pincmdfile import pinCmdFileOps


class internalDriver(busDriver):

   __instance__: [None, object] = None

   @staticmethod
   def init_start(mqtt_que: queue.SimpleQueue) -> bool:
      try:
         if internalDriver.__instance__ is not None:
            return True
         internalDriver.__instance__ = internalDriver(mqtt_que)
         internalDriver.__instance__.start()
         return True
      except Exception as e:
         print(e)
         return False

   def __init__(self, mqtt_que: queue.SimpleQueue):
      super().__init__(busTypes.INTERNAL, mqtt_que)

   def run(self) -> None:
      # -- init code --
      if not self.__init_bus_node_pins__():
         raise Exception("ErrorOnInitBusNodePins")
      # -- end of init --
      while True:
         print("\t -- [ internal_driver.run ] --")
         dts_ms = self.epoch_ms()
         self.print_info()
         self.__loop__()
         # -- sleep --
         loop_sleep = self.loop_delay_secs(dts_ms)
         time.sleep(loop_sleep)

   def __loop__(self):
      for bus in self.driver_buses:
         if not xmlUtils.is_bus_of_type(bus, self.bustype.upper()):
            continue
         self.__on_each_bus__(bus)

   """
      cmd file hold pin number to be used
   """
   def __process_bus_node_cmds__(self, bus_ap: argsParser
         , node_ap: argsParser, node_pins: t.List[et.Element]):
      # -- -- -- --
      bus_adr = int(bus_ap.get_item("id"))
      node_adr = int(node_ap.get_item("address"))
      # -- -- -- --
      for node_pin in node_pins:
         self.__on_each_node_pin__(bus_adr, node_adr, node_pin)
      # -- -- -- --

   def __on_each_node_pin__(self, bus_address, node_address, node_pin: et.Element):
      pin = int(node_pin.attrib["id"])
      # -- full pin address  --
      FULL_PIN_ADDRESS = gpioUtils.full_pin_address(bustype=busTypes.INTERNAL
         , busid=bus_address, nodeid=node_address, pinid=pin)
      # -- build cmd file name --
      cmd_file_name = gpioUtils.cmd_file_name(FULL_PIN_ADDRESS)
      cmd_file_buff = pinCmdFileOps.read(cmd_file_name)
      if cmd_file_buff is False:
         print(f"[ NO_CMD_FILE -> modbus: {bus_address}; node: {node_address}; pin: {pin}; ]")
         return
      # -- --
      # -- compute pin state --
      temp = node_pin.attrib["inverted"]
      pc: pinCMD = pinCMD(FULL_PIN_ADDRESS, cmd_file_buff, temp)
      if not pc.compute_pinval():
         pass
      # -- set & confirm pin --
      on_value = pc.pinval
      print(f"\t ->bus: internal; node: {node_address}; pin: {pin}; val: {on_value}")
      if self.__write_confirm_pin__(pin, on_value):
         pinRuntime.update_pin(pc.pinadr, pc.actcmd, pc.toggle, pc.pinval_str)

   def __init_bus_node_pins__(self) -> bool:
      # -- --
      gpio.setwarnings(False)
      buses = []
      for b in self.driver_buses:
         if not xmlUtils.is_bus_of_type(b, self.bustype.upper()):
            continue
         buses.append(b)
      # -- --
      def on_bus(bus):
         bus_args: argsParser = argsParser(bus)
         # -- set pin mode --
         pinmode: str = bus_args.get_item("pinmode")
         if pinmode.upper() == "BCM":
            gpio.setmode(gpio.BCM)
         # -- end set mode --
         for node in bus.findall("node"):
            busnode: busNode = internalNode(node, bus_args)
            busnode.init_node_pins()
      # -- --
      for _bus in buses:
         on_bus(_bus)
      # -- --
      return True

   def __write_confirm_pin__(self, pin: int, pinval: int) -> bool:
      try:
         gpio.output(pin, pinval)
         return True
      except Exception as e:
         print(e)
         return False
