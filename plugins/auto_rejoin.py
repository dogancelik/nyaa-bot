"""
  Auto Rejoin plugin
  -------------------
  Rejoins the channel if you get kicked from it.
"""
import utils.plugin


def rejoin(server=None, channel=None, **kwargs):
  server.join(channel)

rejoin.settings = {
  'channels': utils.plugin.CHANNELS.ALL,
  'events': ["kick"],
  'users': utils.plugin.USERS.ALL,
  'text': r".*"
}