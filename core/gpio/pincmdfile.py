
import os


CMDS_DIR = "cmds"


class pinCmdFileOps(object):

   @staticmethod
   def write(cmd_file_name: str, buff: bytes) -> bool:
      try:
         if not os.path.exists(CMDS_DIR):
            raise FileNotFoundError(f"NotFound: {CMDS_DIR}")
         # -- cmd file should have ext. --
         rel_path = f"{CMDS_DIR}/{cmd_file_name}"
         with open(rel_path, "w") as f:
            f.write(buff.decode())
         return os.path.exists(rel_path)
      except Exception as e:
         print(e)
         return False

   @staticmethod
   def read(cmd_file_name: str) -> [False, str]:
      try:
         if not os.path.exists(CMDS_DIR):
            raise FileNotFoundError(f"NotFound: {CMDS_DIR}")
         # -- cmd file should have ext. --
         rel_path = f"{CMDS_DIR}/{cmd_file_name}"
         with open(rel_path, "r") as f:
            buff = f.read()
         return buff
      except Exception as e:
         print(e)
         return False

   def __init__(self):
      pass
