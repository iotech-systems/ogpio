#!/usr/bin/env python3

import os, time
from core.gpio.pinruntime import pinRuntime


def main():
   while True:
      os.system("clear")
      pinRuntime.print_table()
      time.sleep(2.0)


# -- entry point --
if __name__ == "__main__":
   main()
