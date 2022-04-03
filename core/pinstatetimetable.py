
import datetime
from core.location import location


class pinStateTimetable(object):

   def __init__(self, cmds: []):
      self.cmds = cmds
      self.active_cmd = None
      self.sysloc = location()

   def is_pin_on_active(self) -> bool:
      # -- reset active cmd --
      self.active_cmd = None
      dt_now = datetime.datetime.now(tz=self.sysloc.timezone())
      dt_now = dt_now.replace(microsecond=0)
      # -- find on time slot --
      for cmd in self.cmds:
         cmdid = cmd["id"]
         dt_on: datetime.datetime = cmd["on"]
         dt_off: datetime.datetime = cmd["off"]
         # -- check times; return on first match --
         if dt_on < dt_now < dt_off:
            self.__print_match__(cmdid, dt_on, dt_now, dt_off, "MATCH!")
            self.active_cmd = cmd
            return True
         # -- this should be run over midnight --
         elif dt_on.hour > dt_off.hour:
            if (dt_on < dt_now) or ((dt_now.hour < dt_off.hour)
                  and (dt_now.minute < dt_off.minute)):
               self.__print_match__(cmdid, dt_on, dt_now, dt_off, "MIDNIGHT MATCH!")
               self.active_cmd = cmd
               return True
      # -- not found --
      return False

   def __print_match__(self, xid: int, on: datetime.datetime
         , now: datetime.datetime, off: datetime.datetime, msg: str):
      print(f"    + + + id: {xid} + + +\n\ton:  {on}")
      print(f"\tnow: {now}")
      print(f"\toff: {off}\n\t-- {msg} --")

   def __time__(self, dt: [datetime.datetime, datetime.time]) -> datetime.time:
      if type(dt) == datetime.datetime:
         _time = dt.time().replace(microsecond=0)
      else:
         _time = dt.replace(microsecond=0)
      # -- return only time --
      return _time
