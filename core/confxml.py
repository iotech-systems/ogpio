
import os.path
import xml.etree.ElementTree as et


XML_FILE = "conf/conf.xml"
CMDS_FOLDER = "cmds"


class confXml(object):

   def __init__(self, path=XML_FILE):
      self.xml = et.parse(path)

   def loc_xml(self) -> et.Element:
      return self.xml.find("location")
