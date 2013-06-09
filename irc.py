import time
import config
import irclib
import sys
import threading
import utils.plugin
import utils.bot
import inspect


class NyaaBot:
  PLUGINS_DIR = "plugins"
  THREADED_EVENTS = ["pubmsg", "pubnotice", "privmsg", "privnotice"]

  irc = irclib.IRC()
  server = irc.server()
  plugins = {}  # Contains all plugins/modules inside commands directory
  handlers = []  # Contains all handlers from imported plugins/modules

  def __init__(self):
    self.app_path = utils.bot.get_dir_path(sys.argv[0])
    self.logger = utils.bot.Logger(config.LOG_LEVEL)
    self.loader = utils.bot.ModuleLoader(self)

    self.load_handlers()
    self.irc.add_global_handler("all_events", self.process_messages)
    self.irc.add_global_handler("disconnect", self.process_disconnect)
    self.irc.add_global_handler("welcome", self.process_connect)
    self.irc.add_global_handler("endofmotd", self.process_ready)

    self.server.connect(config.NETWORK, config.PORT, config.NICK, ircname=config.NAME, ssl=config.USE_SSL)

    self.processor_thread = threading.Thread(target=self.processor)
    self.processor_thread.name = "IRC Processor"
    self.processor_thread.daemon = 1
    self.processor_thread.start()

    if config.WATCH_PLUGINS:
      try:
        handler = utils.bot.PyHandler(self)
        observer = utils.bot.PyWatcher(handler, self.PLUGINS_DIR)
        observer.start()
      except Exception, e:
        self.logger.error("Error when starting when plugins watcher: %s", str(e))
      else:
        self.logger.info("Started plugins watcher")
    else:
      self.logger.info("Plugins watcher is not enabled")

  def processor(self):
    while True:
      self.irc.process_forever()

  def load_handlers(self, reload_modules=False):
    if reload_modules:
      self.loader.remove_all_modules()
    self.loader.add_all_modules(reload_modules)

  def process_messages(self, server, event):
    if event.eventtype() == "all_raw_messages" or event.eventtype() in config.SKIP_EVENTS:
      return

    self.logger.debug("%s: %s - %s: %s" % (event.eventtype(), event.source(), event.target(), event.arguments()))

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

    self.logger.debug("Processing handlers for event %s", event.eventtype())
    for handler in self.handlers:
      function_name = handler[1].__name__
      if event.eventtype() in handler[2]:
        if not ("unused_handlers" in config.HIDE_LOGS):
          self.logger.debug("%s is binded to %s", function_name, event.eventtype())
        if handler[0].match(text):
          if "unused_handlers" in config.HIDE_LOGS:
            self.logger.debug("%s is binded to %s", function_name, event.eventtype())
          self.logger.debug("'%s' matched '%s' for %s", text, handler[0].pattern, function_name)
          channels, users = handler[3:5]

          if event.eventtype() == "pubmsg" or event.eventtype() == "privmsg":
            isvoiceup = ishopup = isopup = None
            if event.eventtype() == "pubmsg":
              isvoiceup = server.hasaccess(channel, nick) or server.isvoice(channel, nick)
              ishopup = server.hasaccess(channel, nick)
              isopup = server.isop(channel, nick)
              self.logger.info("VoiceUp: %s - HopUp: %s - OpUp: %s", isvoiceup, ishopup, isopup)

            self.logger.info("Users: %s - Channels: %s", users, channels)
            if not users == utils.plugin.USERS.ALL:
              if type(users) is list:
                if not nick.lower() in map(lambda x: x.lower(), users):
                  continue
              elif type(users) is int:
                if users == utils.plugin.USERS.OP_UP and not isopup:
                  continue
                elif users == utils.plugin.USERS.HALFOP_UP and not ishopup:
                  continue
                elif users == utils.plugin.USERS.VOICE_UP and not isvoiceup:
                  continue
              else:
                self.logger.error("User bind error: %s", function_name)
                continue

            if not channels == utils.plugin.CHANNELS.ALL:
              if type(channels) == list or type(channels) == set:
                if not channel.lower() in map(lambda x: x.lower(), channels):
                  continue
              else:
                self.logger.error("Channel bind error: %s", function_name)
                continue

          try:
            self.logger.info("Executing %s for %s", function_name, event.eventtype())
            logger = self.logger.getChild(function_name)
            if event.eventtype() in self.THREADED_EVENTS:
              thread = threading.Thread(target=handler[1], kwargs={
                'server': server,
                'nick': nick,
                'channel': channel,
                'text': text,
                'userhost': userhost,
                'logger': logger,
              })
              thread.daemon = True
              thread.start()
            else:
              handler[1](server=server, nick=nick, channel=channel, text=text, userhost=userhost, logger=logger)
          except:
            self.logger.exception("Error when executing %s for %s", function_name, event.eventtype())

  def join_channel(self, channels=config.CHANNELS):
    if type(channels) == str:
      self.server.join(channels)
    elif isinstance(channels, list):
      for channel in channels:
        self.server.join(channel)

  def process_disconnect(self, server, event):
    self.logger.info("Disconnected from server")
    while server.connected == 0:
      self.logger.info("Trying to reconnect to server...")
      try:
        time.sleep(10)
        server.connect(config.NETWORK, config.PORT, config.NICK, ircname=config.NAME)
      except Exception, e:
        self.logger.error("Error '%s' while trying to reconnect", str(e))
        time.sleep(60)

  def process_connect(self, server, event):
    self.logger.info("Connected to server")

  def process_ready(self, server, event):
    if len(config.NICKPWD) > 0:
      server.privmsg("nickserv", "identify %s" % config.NICKPWD)
    self.join_channel()

if __name__ == "__main__":
  nb = NyaaBot()
  cmd = nb.server.send_raw
  r = lambda: nb.load_handlers(True)