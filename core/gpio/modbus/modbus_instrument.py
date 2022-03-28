
import minimalmodbus as mm
from core.strucs import serialInfo


class modbusInstrument(mm.Instrument):

   """
      mode:= mm.MODE_RTU
   """
   def __init__(self, sinfo: serialInfo = None, ttydevice: str = None
         , busnode: int = None, mode: str = None):
      # -- --
      super().__init__(ttydevice, busnode, mode)
      if sinfo is not None:
         self.set_serial_info(sinfo)
      self.clear_buffers_before_each_transaction = True

   def set_serial_info(self, sinfo: serialInfo):
      self.serial.baudrate = sinfo.baudrate
      self.serial.stopbits = sinfo.stopbits
      self.serial.parity = sinfo.parity
      self.serial.timeout = sinfo.timeout
