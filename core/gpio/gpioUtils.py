
"""
   pin topic: omms/rpi3_3relay/gpio/bus/internal/00/node/000/pin/26/cmd
   cmd file name: internal_00_node_000_pin_00.json
      [bustype:0]_[busid:1]_node_[nodeid:2]_pin_[pinid:3].json
   omms/rpi3_3relay/gpio/bus/internal/000/node/000/pin/026/cmd
"""


class gpioUtils(object):

   PIN_ADDRESS_TEMPLATE = "D#%s#B%03d#N%03d#P%03d"
   PIN_TOPIC_TEMPLATE = "omms/%s/gpio/bus/%s/%03d/node/%03d/pin/%03d/cmd"

   @staticmethod
   def full_pin_address(**kwargs):
      if "topic" in kwargs:
         arr = str(kwargs["topic"]).split("/")
         btype = arr[4]
         bid = int(arr[5])
         nodeid = int(arr[7])
         pinid = int(arr[9])
      else:
         btype = kwargs["bustype"]
         bid = int(kwargs["busid"])
         nodeid = int(kwargs["nodeid"])
         pinid = int(kwargs["pinid"])
      # -- return cmd file name --
      btype = btype.upper()
      return gpioUtils.PIN_ADDRESS_TEMPLATE % (btype, bid, nodeid, pinid)

   @staticmethod
   def cmd_file_name(pull_pin_adr: str):
      return f"{pull_pin_adr}.PINCMD"

   @staticmethod
   def pin_topic(hn: str, btype: str, bid: int, nid: int, pin: int):
      """
         :param hn: hostname
         :param btype: bus type
         :param bid: bus id
         :param nid: node id
         :param pin: pin id/number
         :return: mqtt_clt topic string
      """
      return gpioUtils.PIN_TOPIC_TEMPLATE % (hn, btype, bid, nid, pin)

   def __init__(self):
      pass
