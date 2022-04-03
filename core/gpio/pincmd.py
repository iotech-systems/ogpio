
import datetime, json
import xml.etree.ElementTree as et
from core.utils import utils
from core.location import location
from core.pinstatetimetable import pinStateTimetable
from core.strucs import pinToggle, cmd, gpioTime


CMDS_DIR = "cmds"
PARTS_OF_DAY = ["SUNSET", "SUNRISE", "DAWN", "DUSK", "NOON"]


class pinCMD(object):

   PIN_TOGGLE_TABLE = {}
   NO_TOGGLE = "toggle[]"

   def __init__(self, pin_full_adr: str, jsbuff: str, invert: str):
      # -- --
      self.pin_full_adr = pin_full_adr
      self.jsbuff = jsbuff
      self.is_inverted = self.__set_inverted__(invert)
      self.jscmd = json.loads(self.jsbuff)
      self.sysloc = location()
      self.__pinval: [None, bool] = False
      self.__actcmd: str = ""
      self.__toggle: str = pinCMD.NO_TOGGLE

   def __int__(self, pinxml: et.Element, cmdbuff: str):
      self.pinxml: et.Element = pinxml
      self.cmdbuff = cmdbuff

   @property
   def pinval(self) -> bool:
      if self.__pinval is None:
         raise ValueError("[ compute_pin_val was not called ]")
      # -- --
      if self.is_inverted:
         valout = not self.__pinval
      else:
         valout = self.__pinval
      # -- update table --
      return valout

   @property
   def pinval_str(self) -> str:
      val = self.pinval
      if self.is_inverted:
         val = (not val)
      # -- return string --
      return "on" if val else "off"

   @property
   def actcmd(self) -> str:
      return self.__actcmd

   @property
   def toggle(self) -> str:
      return self.__toggle

   @property
   def pinadr(self) -> str:
      return self.pin_full_adr

   def compute_pinval(self) -> bool:
      try:
         # -- test if jscmd is numeric --
         if self.jsbuff.strip().isnumeric():
            self.__pinval = False if self.jsbuff in [0, "0"] else True
            self.__actcmd = self.jsbuff
            return True
         # -- compute if json --
         override: str = self.jscmd["override"]
         if override.upper() in ["ON", "OFF", "0", "1"]:
            self.__pinval = utils.pin_bool_val(override)
            self.__actcmd = f"override: {override.upper()}"
            # self.__toggle = ""
         else:
            boolval, actcmd, toggle = self.__compute_boolean_state__()
            self.__pinval = boolval
            self.__actcmd = actcmd
            self.__toggle = toggle
         # -- return true --
         return True
      except Exception as e:
         print(e)
         return False

   def __compute_boolean_state__(self) -> (bool, str, str):
      arr: [] = self.__pin_timetable__()
      table = pinStateTimetable(arr)
      # -- is pin in "on/active" period --
      if not table.is_pin_on_active():
         return False, "", pinCMD.NO_TOGGLE
      # -- get active cmd time period --
      obj_cmd: cmd = cmd(self.pin_full_adr, table.active_cmd)
      # -- pin is "on/active" -> check if is onday --
      if not self.__is_on_day__(obj_cmd):
         return False, "", pinCMD.NO_TOGGLE
      # -- pin is in "on/active" -> check if toggle attrib is set --
      toggle_state, toggle = self.__toggle_state__(obj_cmd)
      return toggle_state, str(obj_cmd), str(toggle)

   def __pin_timetable__(self) -> []:
      # -- offset can only be applied to sun based dt --
      arrout = []
      # -- json object/dict --
      cmds = self.jscmd["cmds"]
      for _cmd in cmds:
         dt_on: datetime.datetime; dt_off: datetime.datetime
         # -- time on --
         on: str = _cmd["on"]
         if on.upper() in PARTS_OF_DAY:
            tmp_str: str = _cmd["on_offset_mnts"]
            on_offset: int = 0 if tmp_str == "" else int(tmp_str)
            dt_on = self.sysloc.from_part_of_day(on.lower(), on_offset)
         else:
            dt_on = self.__str_to_dt__(on)
         _cmd["on"] = dt_on
         # -- time off --
         off: str = _cmd["off"]
         if off.upper() in PARTS_OF_DAY:
            tmp_str: str = _cmd["off_offset_mnts"]
            off_offset: int = 0 if tmp_str == "" else int(tmp_str)
            dt_off = self.sysloc.from_part_of_day(off.lower(), off_offset)
         else:
            dt_off = self.__str_to_dt__(off)
         _cmd["off"] = dt_off
         # ---
         # -- check if off is pass midnight; if true + 1 day to off --
         # ---
         if dt_off.hour < dt_on.hour:
            _cmd["off"] = (dt_off + datetime.timedelta(days=1))
         # -- load to arrout --
         arrout.append(_cmd)
      # -- return table --
      return arrout

   def __str_to_dt__(self, dtstr: str) -> datetime.datetime:
      try:
         now = datetime.date.today()
         y, m, d = now.year, now.month, now.day
         h, mn = dtstr.split(":")
         # -- set datetime; assume runs on a day of action --
         dt = datetime.datetime(year=y, month=m, day=d, hour=int(h)
            , minute=int(mn), second=0, microsecond=0, tzinfo=self.sysloc.timezone())
         return dt
      except Exception as e:
         print(e)

   def __str_to_time__(self, timestr: str) -> datetime.time:
      try:
         hr, mn = timestr.split(":")
         # -- create time object --
         _time = datetime.time(hour=int(hr), minute=int(mn), second=0
            , microsecond=0, tzinfo=self.sysloc.timezone())
         return _time
      except Exception as e:
         print(e)

   def __gpio_time__(self, timestr) -> gpioTime:
      try:
         hr, mn = [int(x) for x in timestr.split(":")]
         return gpioTime(hr, mn)
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

   def __toggle_state__(self, obj_cmd: cmd) -> (bool, pinToggle):
      try:
         # -- --
         if obj_cmd.toggle in [None, False, {}]:
            return True, pinCMD.NO_TOGGLE
         # -- do toggle logic --
         pt: pinToggle = pinToggle(obj_cmd.toggle)
         if pt.toggle_id not in pinCMD.PIN_TOGGLE_TABLE.keys():
            pinCMD.PIN_TOGGLE_TABLE[pt.toggle_id] = pt
         else:
            xpt: pinToggle = pinCMD.PIN_TOGGLE_TABLE[pt.toggle_id]
            if xpt.toggle_hash != pt.toggle_hash:
               pinCMD.PIN_TOGGLE_TABLE[pt.toggle_id] = pt
         # -- do pin toggle --
         pt: pinToggle = pinCMD.PIN_TOGGLE_TABLE[pt.toggle_id]
         # -- if on --
         if pt.state and pt.on_expired():
            pt.toggle()
         # -- if off --
         if not pt.state and pt.off_expired():
            pt.toggle()
         # -- return new state --
         return pt.state, pt
      except Exception as e:
         print(e)
         return False, ""

   def __set_inverted__(self, anyval: str) -> bool:
      return anyval.upper() in ["Y", "YES"]

   def __sun_name_offset__(self, name: str, state: str):
      pass
