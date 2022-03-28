
import datetime
from core.location import location


class pinStateTable(object):

   def __init__(self, cmds: []):
      self.cmds = cmds
      self.active_cmd = None
      self.sysloc = location()

   def is_pin_on_active(self) -> bool:
      # -- reset active cmd --
      self.active_cmd = None
      now = datetime.datetime.now(tz=self.sysloc.timezone())
      # -- find on time slot --
      for cmd in self.cmds:
         xid = cmd["id"]
         on = self.__time__(cmd["on"])
         off = self.__time__(cmd["off"])
         time_now = self.__time__(now)
         # -- check times --
         if on < time_now < off:
            self.__print_match__(xid, on, time_now, off, "MATCH!")
            self.active_cmd = cmd
            return True
         else:
            pass
      # -- not found --
      return False

   def __print_match__(self, xid: int, on: datetime.time
         , now: datetime.time, off: datetime.time, msg: str):
      print(f"    + + + id: {xid} + + +\n\ton: {on}")
      print(f"\tnow: {now}")
      print(f"\toff: {off}\n\t-- {msg} --")

   def __time__(self, dt: [datetime.datetime, datetime.time]) -> datetime.time:
      if type(dt) == datetime.datetime:
         _time = dt.time().replace(microsecond=0)
      else:
         _time = dt.replace(microsecond=0)
      # -- return only time --
      return _time
