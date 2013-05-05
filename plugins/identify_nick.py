import config

def identify(server=None, **kwargs):
  server.privmsg('nickserv', 'identify %s' % config.NICKPWD)

identify.settings = {
  "events": ["endofmotd"],
  "text": r".*",
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.ALL
}