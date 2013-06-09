"""
  CTCP Reply plugin
  This is required on Rizon IRC Network.
"""
import utils.plugin


def reply(server=None, nick=None, **kwargs):
  server.ctcp_reply(nick, "VERSION irclib 4.8")


reply.settings = {
  'channels': utils.plugin.CHANNELS.ALL,
  'events': ["ctcp"],
  'users': utils.plugin.USERS.ALL,
  'text': r"VERSION"
}