
import datetime, time, json, hashlib
import xml.etree.ElementTree as et


class busTypes(object):

   MODBUS = "MODBUS"
   INTERNAL = "INTERNAL"

class driverTypes(object):

   MQTT = "mqtt"
   REST = "rest"

class mqttLoops(object):

   FOREVER = "FOREVER"
   START = "START"


class mqttInfo(object):

   def __init__(self, host, port, pwd, uid):
      self.host = host
      self.port = port
      self.pwd = pwd
      self.uid = uid


class pinStateEvents(object):

   INIT: str = "initialize"
   STATE_CHANGE: str = "state_change"


class channelPinStateEvent(object):

   def __init__(self, mqttinfo: mqttInfo, pin_event: str
         , channel_id, pin_id, val):
      self.mqttinfo = mqttinfo
      self.pin_event = pin_event
      self.channel_id: int = channel_id
      self.pin_id: int = pin_id
      self.val = val

   def __repr__(self):
      return f"Channel: {self.channel_id}; Pin: {self.pin_id}; Value: {self.val};"

class pinStateEvent(object):

   def __init__(self, mqttinfo: mqttInfo, bustype: str, busid: int
         , nodeid: int, pinid: int, pinval: int):
      self.mqttinfo = mqttinfo
      self.bustype = bustype
      self.busid = busid
      self.nodeid = nodeid
      self.pinid = pinid
      self.pinval = pinval

   def __repr__(self):
      return f"pinStateEvent: "


class pinToggle(object):

   def __init__(self, tobj: {}):
      self.tobj = tobj
      self.toggle_id = self.tobj["toggle_id"]
      self.toggle_hash = self.tobj["toggle_hash"]
      self.state: bool = bool(self.tobj["init"])
      self.on_secs: int = self.__secs__(self.tobj["on"])
      self.off_secs: int = self.__secs__(self.tobj["off"])
      self.dts_secs: int = int(time.time())

   def __hash__(self):
      return f"{self.state}:{self.on_secs}:{self.off_secs}"

   def __repr__(self):
      return f"toggle[on: {self.on_secs}s; off: {self.off_secs}s;]"

   def update_dts_secs(self):
      self.dts_secs: int = int(time.time())

   def toggle(self):
      self.state = not self.state
      self.update_dts_secs()
      print(f"\n\t -- pinToggle.toggle -> s: {self.state}; dts: {self.dts_secs}; --\n")

   def on_expired(self) -> bool:
      secs: int = int(time.time())
      return (secs - self.dts_secs) > self.on_secs

   def off_expired(self) -> bool:
      secs: int = int(time.time())
      return (secs - self.dts_secs) > self.off_secs

   def md5(self) -> str:
      buff = f"{self.toggle_id}:{self.state}:{self.on_secs}:{self.off_secs}"
      return str(hashlib.md5(buff)).upper()

   def __secs__(self, buff: str) -> int:
      buff = buff.lower()
      if "m" in buff:
         n = int(buff.replace("m", ""))
         return n * 60
      elif "h" in buff:
         n = int(buff.replace("h", ""))
         return n * 3600
      else:
         n = int(buff.replace("s", ""))
         n = 59 if n > 60 else n
         return n


class cmd(object):

   def __init__(self, pinadr: str, cmdDict: {}):
      self.pinadr = pinadr
      self.cmdDict = cmdDict
      self.id = None
      self.on: [None, datetime.time] = None
      self.off: [None, datetime.time] = None
      # -- this needs to me revisited --
      self.on_offset_mnts = None
      self.off_offset_mnts = None
      self.ondays: str = ""
      self.toggle = None
      self.__set_vals__()

   def __str__(self):
      return f"on: {self.on}; off: {self.off}; days: {self.ondays};"

   def __set_vals__(self):
      # - - set keys - -
      _init, _on, _off = "init", "on", "off"
      # print(f"__set_vals__\n{self.cmdDict}")
      self.objtype = self.cmdDict["_objtype"]
      self.id = self.cmdDict["id"]
      self.on = self.cmdDict["on"]
      self.off = self.cmdDict["off"]
      self.on_offset_mnts = self.cmdDict["on_offset_mnts"]
      self.off_offset_mnts = self.cmdDict["off_offset_mnts"]
      if "ondays" in self.cmdDict:
         self.ondays = self.cmdDict["ondays"]
      # - - if toggle - -
      if "toggle" in self.cmdDict:
         t: dict = self.cmdDict["toggle"]
         if t is not None and ({_init, _on, _off} <= t.keys()):
            t["toggle_id"] = self.pinadr
            t["toggle_hash"] = f"{t[_init]}:{t[_on]}:{t[_off]}"
            self.toggle = t
         else:
            pass
      # - - - - - - - -

class argsParser(object):

   delimiter = ";"
   assign_symbol = ":="

   def __init__(self, elmt: et.Element):
      if "args" not in elmt.attrib:
         raise ValueError(f"BadXmlElement: {elmt.tag}")
      # -- process element --
      self.element_tag = elmt.tag
      self._buff = elmt.attrib["args"]
      self._dict = {}
      self._arr: [] = []
      self.__load_dict__()

   @property
   def dictionary(self):
      return self._dict

   def get_item(self, key: str) -> [False, object]:
      if key not in self._dict.keys():
         return False
      _t = self._dict[key]
      return _t

   def get_hash(self) -> str:
      md5 = hashlib.md5(self._buff.encode())
      return md5.hexdigest()

   def __load_dict__(self):
      self._arr = self._buff.split(argsParser.delimiter)
      for kv in self._arr:
         if kv == "":
            break
         k, v = kv.split(argsParser.assign_symbol)
         self._dict[k] = v


class serialInfo(object):

   def __init__(self, args: str):
      self.args = args
      self.baudrate = 9600
      self.charbits = 8
      self.stopbits = 1
      self.parity = "N"
      self.__parse__()

   """
      -- baudrate, settings, timeout
      -- 9600:8N1:45 --
   """
   def __parse__(self):
      arr = self.args.split(":")
      if len(arr) != 3:
         raise ValueError(f"MissingInput: {self.args}")
      self.baudrate = int(arr[0])
      self.charbits: int = int(arr[1][0])
      self.parity = arr[1][1]
      self.stopbits = int(arr[1][2])
      self.timeout = int(arr[2])
