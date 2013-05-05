import config

def nyaauth(server, nick):
  server.join("#nyaa-nyaa")
  if server.hasaccess("#nyaa-nyaa", nick):
    return True
  return False

def join(server=None, nick=None, text=None, **kwargs):
  for ch in text.split(" ", 1)[1].split(" "):
    server.join(ch)

def part(server=None, nick=None, text=None, **kwargs):
  if nyaauth(server, nick) is False:
    return
  server.part([text.split(' ', 1)[1]], u"Leaving")

def nick(server=None, text=None, **kwargs):
  server.nick(text.split(' ', 1)[1])

def say(server=None, text=None, **kwargs):
  rcommand, rchannel, rmessage = text.split(' ', 2)
  server.privmsg(rchannel, rmessage)

def action(server=None, text=None, **kwargs):
  rcommand, rchannel, rmessage = text.split(' ', 2)
  server.action(rchannel, rmessage)

join.settings = {
  "events": config.EVENTS.PRIVMSG,
  "text": r'join.*',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.ALL
}

part.settings = {
  "events": config.EVENTS.PRIVMSG,
  "text": r'part.*',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.ALL
}

nick.settings = {
  "events": config.EVENTS.PRIVMSG,
  "text": r'nick.*',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.DEV
}

say.settings = {
  "events": config.EVENTS.PRIVMSG,
  "text": r'say.*',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.DEV
}

action.settings = {
  "events": config.EVENTS.PRIVMSG,
  "text": r'act(ion)?.*',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.DEV
}
