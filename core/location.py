
from astral.sun import sun
import datetime, astral, pytz
import xml.etree.ElementTree as et
from core.confxml import confXml
from datetime import tzinfo
from core.strucs import gpioTime


class location(object):

   def __init__(self, elm: et.Element = None):
      self.locxml: et.Element = self.__locxml__(elm)
      self.name = self.locxml.attrib["name"]
      self.lat = float(self.locxml.attrib["lat"])
      self.lng = float(self.locxml.attrib["lng"])
      self.country = self.locxml.attrib["country"]
      self.country_code = self.locxml.attrib["countrycode"]
      self.tz_str = pytz.country_timezones[self.country_code][0]
      self.tz_boj = self.__set_tz__()
      self.city = astral.LocationInfo(name=self.name, region=self.country
         , timezone=self.tz_str, latitude=self.lat, longitude=self.lng)
      self.sun = self.__sun__()

   def dump(self):
      print(self.sun)

   def from_part_of_day(self, name: str, offset: int = 0) -> datetime.datetime:
      if name not in self.sun:
         raise ValueError(f"BadKeyName: {name}")
      # -- compute datetime --
      if -90 > offset > 90:
         raise ValueError(f"OutOfRangeOffsetValue: {offset}")
      # -- --
      sun_dt = self.sun[name]
      # sun_dt = self.__clean_dt__(sun_dt)
      dt = (sun_dt + datetime.timedelta(minutes=offset))
      # -- return --
      return dt.replace(second=0, microsecond=0)

   def part_of_day(self, name: str, offset: int) -> [None, gpioTime]:
      if name not in self.sun:
         raise ValueError(f"BadKeyName: {name}")
      # -- check time offset --
      if -90 > offset > 90:
         raise ValueError(f"OutOfRangeOffsetValue: {offset}")
      # -- compute datetime --
      sun_dt = self.sun[name]
      sun_dt = self.__clean_dt__(sun_dt)
      dt = sun_dt + datetime.timedelta(minutes=offset)
      _time = dt.time()
      return self.__gpio_time__(_time)

   def timezone(self) -> tzinfo:
      return self.tz_boj

   def __sun__(self) -> sun:
      utcnow = datetime.datetime.utcnow()
      return sun(self.city.observer, date=utcnow, tzinfo=self.tz_str)

   def __locxml__(self, elmt: et.Element) -> et.Element:
      if elmt is not None:
         return elmt
      # -- create default --
      confxml = confXml()
      return confxml.loc_xml()

   def __set_tz__(self) -> tzinfo:
      xdt = datetime.datetime.utcnow()
      return pytz.timezone(zone=self.tz_str).localize(dt=xdt).tzinfo

   def __clean_dt__(self, dt: datetime.datetime) -> datetime.datetime:
      dt = dt.replace(microsecond=0)
      return dt

   def __gpio_time__(self, t: datetime.time) -> gpioTime:
      return gpioTime(t.hour, t.min)
