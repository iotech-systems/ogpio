
from datetime import datetime, timedelta

n = datetime.now()
on_hr, on_mnt = (15, 28)
off_hr, off_mnt = (3, 00)

ACTIVE_ON = datetime(n.year, n.month, n.day, on_hr, on_mnt, 0, 0)
if on_hr > off_hr:
   # -- create new n with +1 day --
   n = n + timedelta(days=1)
ACTIVE_OFF = datetime(n.year, n.month, n.day, off_hr, off_mnt, 0, 0)

if ACTIVE_ON < datetime.now() < ACTIVE_OFF:
   print("on")
else:
   print("off")
