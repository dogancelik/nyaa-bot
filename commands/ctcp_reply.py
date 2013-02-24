import config

def reply(server=None, nick=None, **kwargs):
  server.ctcp_reply(nick, 'VERSION irclib 4.8')

reply.settings = {
  "channels": config.CHANNELS.ALL,
  "events": "ctcp",
  "users": config.USERS.ALL,
  "text": r"VERSION"
}