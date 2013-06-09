"""
  Utils for plugins
"""


class USERS:
  """
    USERS is both used in plugins and in bot

    Only the first 4 is supported right now (``ALL``, ``OP_UP``, ``HALFOP_UP``, ``VOICE_UP``)
  """
  ALL, OP_UP, HALFOP_UP, VOICE_UP, OP_ONLY, HALFOP_ONLY, VOICE_ONLY, NORMAL_ONLY = range(8)


class EVENTS:
  """
    EVENTS is used in plugins

    Constants are put in a list because it is easy to add them and support multiple events at once.
  """
  PUBMSG = ["pubmsg"]
  ACTION = ["action"]
  PRIVMSG = ["privmsg"]


class CHANNELS:
  """
    CHANNELS is used in plugins
  """
  ALL = 0