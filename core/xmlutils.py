
import typing as t
import xml.etree.ElementTree as et
from core.strucs import argsParser


class xmlUtils(object):

   @staticmethod
   def args_parser_from_xml(xmlElm: et.Element) -> [None, argsParser]:
      if xmlElm is None:
         return None
      ap: argsParser = argsParser(xmlElm)
      return ap

   @staticmethod
   def bus_nodes_from_driver():
      pass

   @staticmethod
   def is_bus_of_type(bus: et.Element, mbtype: str) -> bool:
      # -- if bus is enabled==0 exclude from process --
      if int(bus.attrib["enabled"]) == 0:
         return False
      # -- check type --
      bustype = bus.attrib["type"].upper()
      if bustype != mbtype.upper():
         print(f"BAD_BUS_TYPE: {bustype}")
         return False
      # -- return bus is ok --
      return True

   @staticmethod
   def get_nodes_element(xpath: str):
      pass

   @staticmethod
   def get_elements_from_elmt_arr(xpath: str, elmts: t.List[et.Element]):
      pass

   def __init__(self):
      pass
