import time
import config
import irclib
import types
import os
import importlib
import sys
import copy
import re
import threading
import logging
import inspect

logger = logging.getLogger()
logger.setLevel(config.LOGLEVEL)

log_fh = logging.FileHandler("error.log")
log_fh.setLevel(logging.ERROR)
logger.addHandler(log_fh)

log_sh = logging.StreamHandler()
logger.addHandler(log_sh)

log_formatter = logging.Formatter("%(asctime)s %(name)-8s %(levelname)-8s %(message)s", "%m-%d %H:%M")
log_fh.setFormatter(log_formatter)
log_sh.setFormatter(log_formatter)

sublogger = logger.getChild("sub")


class nyaabot:
  PLUGINS_DIR = "plugins"

  irc = irclib.IRC()
  server = irc.server()
  plugins = {}  # Contains all plugins/modules inside commands directory
  handlers = []  # Contains all handlers from imported plugins/modules

  def __init__(self):
    self.load_handlers()
    self.irc.add_global_handler("all_events", self.process_messages)
    self.irc.add_global_handler("disconnect", self.process_disconnect)
    self.irc.add_global_handler("welcome", self.process_connect)
    self.irc.add_global_handler("endofmotd", self.process_ready)

    self.server.connect(config.NETWORK, config.PORT, config.NICK, ircname=config.NAME)

    self.processor_thread = threading.Thread(target=self.processor)
    self.processor_thread.name = "IRC Processor"
    self.processor_thread.daemon = 1
    self.processor_thread.start()

  def processor(self):
    while True:
      self.irc.process_forever()

  def load_handlers(self, reload_modules=False):
    if reload_modules:
      self.handlers = []
      for plugin in copy.copy(self.plugins):
        try:
          logger.debug("Reloading module: %s", plugin)
          del sys.modules[plugin]
        except Exception, e:
          logger.error("Error '%s' while reloading plugin '%s'", str(e), plugin)
        else:
          logger.info("Reloaded module: %s", plugin)
      self.plugins = {}

    the_file = sys.argv[0]  # __file__ (win32)
    main_path = os.path.dirname(os.path.abspath(the_file))
    for (paths, dirs, files) in os.walk(os.path.join(main_path, self.PLUGINS_DIR)):
      files = [f for f in files if f.endswith(".py") and not f.startswith("__")]
      abs_path = paths  # because we use os.path.join(main_path, self.PLUGINS_DIR) in walk
      rel_path = os.path.relpath(paths, main_path)
      logger.debug("Current dir: %s", abs_path)
      logger.debug("Found modules: %s", files)
      for command_file in files:
        file_name = os.path.basename(command_file)[:-3]
        module_name = re.sub(r"[\\/]", ".", rel_path) + "." + file_name
        logger.debug("Loading module: %s", command_file)
        try:
          self.plugins[module_name] = importlib.import_module(module_name)
        except Exception, e:
          logger.error("Error in module (%s): %s" % (file_name, str(e)))
          raise e
          sys.exit(1)
        else:
          logger.info("Imported module: %s", module_name)

    for plugin in self.plugins:
      module = self.plugins[plugin]
      logger.debug("Inspecting module for handlers: %s", module.__name__)
      for function_name in dir(module):
        function = getattr(module, function_name)
        if type(function) == types.FunctionType:
          try:
            settings = getattr(function, "settings")
          except AttributeError:
            pass
          else:
            self.handlers.append(
              (re.compile(settings["text"], re.I | re.U),
              function,
              settings["events"],
              settings["channels"],
              settings["users"])
            )
            logger.debug("Loaded handler: %s" % function_name)

  def process_messages(self, server, event):
    if event.eventtype() == "all_raw_messages":
      return

    logger.debug("%s: %s - %s: %s" % (event.eventtype(), event.source(), event.target(), event.arguments()))

    nick = userhost = host = event.source()
    try:
      if '!' in event.source():
        nick = irclib.nm_to_n(event.source())
        userhost = irclib.nm_to_uh(event.source())
        host = irclib.nm_to_h(event.source())
    except:
      pass
    channel = event.target()
    if event.eventtype() == "pubmsg":
      text = event.arguments()[0]
    elif event.eventtype() == "namreply":
      text = event.arguments()[2]
    else:
      text = event.arguments()[0] if len(event.arguments()) > 0 else ""

    logger.debug("Processing handlers for event %s", event.eventtype())
    #, ", ".join([x[1].__name__ for x in self.handlers]))
    for handler in self.handlers:
      function_name = handler[1].__name__
      if event.eventtype() in handler[2]:
        logger.debug("%s is binded to %s", function_name, event.eventtype())
        if handler[0].match(text):
          logger.debug("'%s' matched '%s' for %s", text, handler[0].pattern, function_name)
          channels, users = handler[3:5]

          if event.eventtype() == "pubmsg" or event.eventtype() == "privmsg":
            isvoiceup = ishopup = isopup = None
            if event.eventtype() == "pubmsg":
              isvoiceup = server.hasaccess(channel, nick) or server.isvoice(channel, nick)
              ishopup = server.hasaccess(channel, nick)
              isopup = server.isop(channel, nick)
              logger.debug("VoiceUp: %s - HopUp: %s - OpUp: %s", isvoiceup, ishopup, isopup)

            logger.debug("Users: %s - Channels: %s", users, channels)
            if not users == config.USERS.ALL:
              if type(users) is list:
                if not nick.lower() in map(lambda x: x.lower(), users):
                  continue
              elif type(users) is int:
                if users == config.USERS.OP_UP and not isopup:
                  continue
                elif users == config.USERS.HALFOP_UP and not ishopup:
                  continue
                elif users == config.USERS.VOICE_UP and not isvoiceup:
                  continue
              else:
                logger.error("User bind error: %s", function_name)
                continue

            if not channels == config.CHANNELS.ALL:
              if type(channels) == list or type(channels) == set:
                if not channel in channels:
                  continue
              else:
                logger.error("Channel bind error: %s", function_name)
                continue

          try:
            logger.debug("Executing %s for %s", function_name, event.eventtype())
            handler[1](server=server, nick=nick, channel=channel, text=text, userhost=userhost, sublogger=sublogger)
          except:
            logger.exception("Error when executing %s for %s", function_name, event.eventtype())

  def join_channel(self, channels=config.CHANNELS.INIT):
    if type(channels) == str:
      self.server.join(channels)
    elif isinstance(channels, list):
      for channel in channels:
        self.server.join(channel)

  def process_disconnect(self, server, event):
    logger.info("Disconnected from server")
    while server.connected == 0:
      logger.info("Trying to reconnect to server...")
      try:
        server.connect(config.NETWORK, config.PORT, config.NICK, ircname=config.NAME)
      except Exception, e:
        logger.error("Error '%s' while trying to reconnect", str(e))
        time.sleep(60)

  def process_connect(self, server, event):
    logger.info("Connected to server")

  def process_ready(self, server, event):
    if len(config.NICKPWD) > 0:
      server.privmsg('nickserv', 'identify %s' % config.NICKPWD)
    self.join_channel()

if __name__ == "__main__":
  nb = nyaabot()
  cmd = nb.server.send_raw
  r = lambda: nb.load_handlers(True)