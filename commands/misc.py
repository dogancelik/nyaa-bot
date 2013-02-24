import config

def help(server=None, channel=None, **kwargs):
  server.privmsg(channel, "http://nyaa-nyaa.com/bot")

help.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r"\.help",
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}

def watch_nick(nick=None, text=None, **kwargs):
  pass

watch_nick.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r".*",
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}