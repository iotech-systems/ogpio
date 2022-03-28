
import datetime
import os, sqlite3
import core.gpio.pincmd as pcmd


IOTECH_RAMDSK = "/opt/iotech/ramdsk"
PIN_DB = "pins.db"


def db_exe_close(_conn: sqlite3.Connection, _qry: str, _commit: bool = True):
   try:
      _cur = _conn.cursor()
      _cur.execute(_qry)
      if _commit:
         _cur.connection.commit()
      _cur.connection.close()
   except Exception as e:
      print(e)


if not os.path.exists(IOTECH_RAMDSK):
   # -- try to create it --
   pass
else:
   _full_path = f"{IOTECH_RAMDSK}/{PIN_DB}"
   if not os.path.exists(_full_path):
      print("--- [ creating pin db file ] ---")
      conn = sqlite3.connect(_full_path)
      qry = "create table pins (pinadr TEXT PRIMARY KEY, cmd TEXT, toggle TEXT, pinval TEXT);"
      db_exe_close(conn, qry)


class pinRuntime(object):

   @staticmethod
   def update_pin(pinid: str, cmd: str, toggle: str, pinval: str):
      try:
         full_path = f"{IOTECH_RAMDSK}/{PIN_DB}"
         tmpl = f"insert into pins values('%s', '%s', '%s', '%s') on " \
            f"conflict (pinadr) do update set cmd = '%s', toggle = '%s', pinval = '%s';"
         sql = tmpl % (pinid, cmd, toggle, pinval, cmd, toggle, pinval)
         # --- print(sql) ---
         conn = sqlite3.connect(full_path)
         db_exe_close(conn, sql)
      except Exception as e:
         print(f"\n -- {e} --\n")

   @staticmethod
   def print_table():
      try:
         full_path = f"{IOTECH_RAMDSK}/{PIN_DB}"
         print("\n   - - - [ pin table dump ] - - -\n")
         now = str(datetime.datetime.now().time()).split(".")[0]
         print(f"     dts: {now}\n")
         conn = sqlite3.connect(full_path)
         cur = conn.cursor()
         for row in cur.execute("select * from pins;"):
            print(f"     -> {row}")
         conn.close()
         print("\n   - - - - - - - - - - - -")
      except Exception as e:
         print(f"\n -- {e} --\n")

   def __init__(self):
      pass
