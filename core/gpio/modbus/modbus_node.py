import time
import typing as t
import minimalmodbus as mm
import xml.etree.ElementTree as et
from core.gpio.modbus.modbus_instrument import modbusInstrument
from core.utils import utils
from core.strucs import serialInfo, argsParser


class modbusNode(object):

   def __init__(self, nodexml: et.Element, busargs: argsParser):
      self.nodexml = nodexml
      self.busargs = busargs
      self.selfargs = argsParser(self.nodexml)
      self.sinfo: serialInfo = serialInfo(self.selfargs.dictionary["settings"])
      self.mbinst: [None, modbusInstrument] = None

   def init_pins(self):
      try:
         # -- setup modbus instrument --
         ttydev = utils.ttyusb(self.busargs)
         node_address = int(self.selfargs.get_item("address"))
         self.mbinst: modbusInstrument = \
            modbusInstrument(None, ttydev, node_address, mm.MODE_RTU)
         # -- process pins --
         pins: t.List[et.Element] = self.nodexml.findall("pins/pin")
         for pin in pins:
            self.mbinst.set_serial_info(self.sinfo)
            pinid = pin.attrib["id"]
            onstart = pin.attrib["onstart"]
            self.mbinst.write_bit(int(pinid), int(onstart))
            time.sleep(0.20)
      except Exception as e:
         print(e)
