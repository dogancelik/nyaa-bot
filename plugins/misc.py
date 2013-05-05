import config

def help(server=None, channel=None, **kwargs):
  server.privmsg(channel, "http://nyaa-nyaa.com/bot.html")

help.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r"\.help",
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}