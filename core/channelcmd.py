
import datetime, json, os.path
import xml.etree.ElementTree as et
from core.utils import utils
from core.xmlattribs import channelElm
from core.location import location
from core.pinstatetimetable import pinStateTimetable
from core.strucs import pinToggle, cmd


CMDS_DIR = "cmds"
# CMD_FILE = "ch_%02d_cmd.json"
PARTS_OF_DAY = ["SUNSET", "SUNRISE", "DAWN", "DUSK", "NOON"]


class channelCMD(object):

   PIN_TOGGLE_TABLE = {}

   @staticmethod
   def cmd_file(topic: str):
      # -- omms/3cpo/gpio/bus/modbus/00/node/000/pin/00/cmd --
      a = topic.split("/")
      bus_type, bus_id, pin_id = (a[4], a[5], a[6], a[8])
      return f"{bus_type}_{bus_id}_pin_{pin_id}_cmd.json"

   @staticmethod
   def save_cmd(cmd_name: str, buff: bytes) -> bool:
      try:
         if not os.path.exists(CMDS_DIR):
            raise FileNotFoundError(f"NotFound: {CMDS_DIR}")
         cmd_path = channelCMD.cmd_path(cmd_name)
         with open(cmd_path, "w") as f:
            f.write(buff.decode())
         return os.path.exists(cmd_path)
      except Exception as e:
         print(e)
         return False

   @staticmethod
   def load_cmd(channel_id: int) -> str:
      cmd_path = channelCMD.cmd_path(channel_id)
      if not os.path.exists(cmd_path):
         raise FileNotFoundError(f"CmdJsonFileNotFound: {cmd_path}")
      with open(cmd_path, "r") as f:
         buff = f.read()
      return buff

   @staticmethod
   def cmd_path(fn: str) -> str:
      path = f"{CMDS_DIR}/%s" % fn
      return path

   @classmethod
   def create(cls, channel: et.Element) -> [False, object]:
      channel_id = int(channel.attrib[channelElm.ID])
      invert = False
      tmp = channel.attrib[channelElm.INVERTED]
      if tmp.upper() in ["Y", "YES"]:
         invert = True
      buff = channelCMD.load_cmd(channel_id)
      # -- return channelCMD(buff, is_inverted) --
      return channelCMD(channel_id, buff, invert) if buff not in [False, ""] else False

   def __init__(self, channel_id: int, jsbuff: str, invert: bool = False):
      self.channel_id = channel_id
      self.jsbuff = jsbuff
      self.invert = invert
      self.jscmd = json.loads(self.jsbuff)
      self.sysloc = location()
      self.__pinval: [None, bool] = False

   @property
   def pinval(self) -> bool:
      if self.__pinval is None:
         raise ValueError("[compute_pin_val was not called]")
      if self.invert:
         return not self.__pinval
      else:
         return self.__pinval

   @property
   def pinval_str(self) -> str:
      return "off" if self.pinval else "on"

   def compute_pinval(self):
      try:
         override: str = self.jscmd["override"]
         if override.upper() in ["ON", "OFF", "0", "1"]:
            self.__pinval = utils.pin_bool_val(override)
         else:
            tmpval: bool = self.__compute_state_bool__()
            self.__pinval = tmpval
      except Exception as e:
         print(e)

   def __compute_state_bool__(self) -> bool:
      arr: [] = self.__state_table__()
      table = pinStateTimetable(arr)
      # -- is pin in "on/active" period --
      if not table.is_pin_on_active():
         return False
      # -- get active cmd time period --
      obj_cmd: cmd = cmd(self.channel_id, table.active_cmd)
      # -- pin is "on/active" -> check if is onday --
      if not self.__is_on_day__(obj_cmd):
         return False
      # -- pin is in "on/active" -> check if toggle attrib is set --
      return self.__toggle_state__(obj_cmd)

   def __state_table__(self):
      arrout = []
      cmds = self.jscmd["cmds"]
      for cmd in cmds:
         # -- time on --
         on: str = cmd["on"]
         if on.upper() in PARTS_OF_DAY:
            # -- offset can only be applied to sun based dt --
            on_offset: str = cmd["on_offset_mnts"]
            cmd["on"] = self.sysloc.from_part_of_day(on.lower(), on_offset)
         else:
            cmd["on"] = self.__str_dt__(on)
         # -- time off --
         off: str = cmd["off"]
         if off.upper() in PARTS_OF_DAY:
            # -- offset can only be applied to sun based dt --
            off_offset: str = cmd["off_offset_mnts"]
            cmd["off"] = self.sysloc.from_part_of_day(off.lower(), off_offset)
         else:
            cmd["off"] = self.__str_dt__(off)
         # -- load to arrout --
         arrout.append(cmd)
      # -- return table --
      return arrout

   def __str_dt__(self, dtstr: str) -> datetime.datetime:
      try:
         now = datetime.date.today()
         y, m, d = now.year, now.month, now.day
         h, mn = dtstr.split(":")
         # -- set datetime --
         dt = datetime.datetime(year=y, month=m, day=d, hour=int(h)
            , minute=int(mn), second=0, microsecond=0, tzinfo=self.sysloc.timezone())
         return dt
      except Exception as e:
         print(e)

   def __is_on_day__(self, __cmd: cmd) -> bool:
      is_on_day = True
      if __cmd.ondays in [None, ""]:
         return is_on_day
      # -- compute --
      day_idx = datetime.datetime.today().weekday()
      d = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"][day_idx]
      if d not in __cmd.ondays.upper():
         is_on_day = False
      # -- return --
      return is_on_day

   def __toggle_state__(self, obj_cmd: cmd) -> bool:
      try:
         print(f"\n__toggle_state__")
         if obj_cmd.toggle in [None, False, {}]:
            print(f"__cmd.toggle: {obj_cmd.toggle} -> return true")
            return True
         # -- do toggle logic --
         pt: pinToggle = pinToggle(obj_cmd.toggle)
         if pt.toggle_id not in channelCMD.PIN_TOGGLE_TABLE.keys():
            channelCMD.PIN_TOGGLE_TABLE[pt.toggle_id] = pt
         else:
            xpt: pinToggle = channelCMD.PIN_TOGGLE_TABLE[pt.toggle_id]
            if xpt.toggle_hash != pt.toggle_hash:
               channelCMD.PIN_TOGGLE_TABLE[pt.toggle_id] = pt
         # -- do pin toggle --
         pt: pinToggle = channelCMD.PIN_TOGGLE_TABLE[pt.toggle_id]
         print(f"\ncmd_id: {obj_cmd.id}\npt: {pt}\n")
         # -- if on --
         if pt.state and pt.on_expired():
            pt.toggle()
         # -- if off --
         if not pt.state and pt.off_expired():
            pt.toggle()
         # -- return new state --
         return pt.state
      except Exception as e:
         print(e)
         return False
