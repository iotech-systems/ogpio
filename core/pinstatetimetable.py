
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
      time_now = dt_now.replace(microsecond=0).time()
      # -- find on time slot --
      for cmd in self.cmds:
         cmdid = cmd["id"]
         time_on: datetime.time = cmd["on"].time()
         time_off: datetime.time = cmd["off"].time()
         # -- check times; return on first match --
         if time_on < time_now < time_off:
            self.__print_match__(cmdid, time_on, time_now, time_off, "MATCH!")
            self.active_cmd = cmd
            return True
         # -- this should be run over midnight --
         elif (time_now > time_on > time_off) \
               or (time_on > time_off > time_now):
            self.__print_match__(cmdid, time_on, time_now, time_off, "MIDNIGHT MATCH!")
            self.active_cmd = cmd
            return True
      # -- not found --
      return False

   def __print_match__(self, xid: int, on: datetime.time
         , now: datetime.time, off: datetime.time, msg: str):
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
