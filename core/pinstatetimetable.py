
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
      dt_now.replace(microsecond=0)
      # -- find on time slot --
      for cmd in self.cmds:
         xid = cmd["id"]
         dt_on: datetime.datetime = cmd["on"]
         dt_off: datetime.datetime = cmd["off"]
         # -- check times --
         if dt_on < dt_now < dt_off:
            self.__print_match__(xid, dt_on, dt_now, dt_off, "MATCH!")
            self.active_cmd = cmd
            return True
         else:
            pass
      # -- not found --
      return False

   def __print_match__(self, xid: int, on: datetime.datetime
         , now: datetime.datetime, off: datetime.datetime, msg: str):
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
