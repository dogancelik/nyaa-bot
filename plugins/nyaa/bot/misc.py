import utils.plugin
import config


def help(server=None, channel=None, **kwargs):
  server.privmsg(channel, "http://nyaa-nyaa.com/bot.html")

help.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': r"\.help",
  'channels': config.MAIN_CHANNELS,
  'users': utils.plugin.USERS.ALL
}