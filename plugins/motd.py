import config

motdtext = """4Welcome to Nyaa-Nyaa!
2To check our latest events visit http://nyaa-nyaa.com/calendar.html
2Enjoy your stay :3"""

def motd(server=None, nick=None, **kwargs):
  if not nick in config.USERS.DEV:
    for line in motdtext.split("\n"):
      server.notice(nick, line)

motd.settings = {
  "events": "join",
  "text": r".*",
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}