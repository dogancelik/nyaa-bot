"""
  *IRC commands* plugin
  ---------------------
  Use ``auth AUTH_PWD`` to authenticate yourself then you can use other commands such as:

  .. warning::

    Change *AUTH_PWD* in :file:`plugins/url_watcher/url_watcher.py` before using this plugin

  ::

    join #this-channel #that-channel
    leave #that-channel
    msg #this-channel Hello
    me #this-channel is AFK
    nick New_Nickname
"""
import utils.plugin

AUTH_PWD = "ChangeThis"  # or use `AUTH_PWD = config.NICKPWD` if you want to use NickServ password
AUTH_USERS = set([])


class BotChat:
  AUTH_SUCCESS = "Authentication successful"
  AUTH_FAIL = "Authentication fail"
  AUTH_NOT = "You have to authenticate yourself first"
  AUTH_ALREADY = "You are already authenticated"


def split_space(text, maxsplit=1):
  return text.split(" ", maxsplit)


def is_authed(nick):
  if nick in AUTH_USERS:
    return True
  return False


def authenticate(nick, password):
  if not nick in AUTH_USERS:
    if password == AUTH_PWD:
      AUTH_USERS.add(nick)
      return True
    return False
  else:
    return None


def auth(server=None, nick=None, text=None, **kwargs):
  res = authenticate(nick, split_space(text)[1])
  if res is True:
    server.privmsg(nick, BotChat.AUTH_SUCCESS)
  elif res is False:
    server.privmsg(nick, BotChat.AUTH_FAIL)
  else:
    server.privmsg(nick, BotChat.AUTH_ALREADY)

auth.settings = {
  'events': utils.plugin.EVENTS.PRIVMSG,
  'text': r"auth .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}


def join(server=None, nick=None, text=None, **kwargs):
  if is_authed(nick):
    for channel in split_space(text)[1].split(" "):
      server.join(channel)
  else:
    server.privmsg(nick, BotChat.AUTH_NOT)

join.settings = {
  'events': utils.plugin.EVENTS.PRIVMSG,
  'text': r"join .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}


def part(server=None, nick=None, text=None, **kwargs):
  if is_authed(nick):
    server.part([split_space(text)[1]], u"Leaving")
  else:
    server.privmsg(nick, BotChat.AUTH_NOT)

part.settings = {
  'events': utils.plugin.EVENTS.PRIVMSG,
  'text': r"(leave|part) .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}


def nick(server=None, nick=None, text=None, **kwargs):
  if is_authed(nick):
    server.nick(split_space(text)[1])
  else:
    server.privmsg(nick, BotChat.AUTH_NOT)

nick.settings = {
  'events': utils.plugin.EVENTS.PRIVMSG,
  'text': r"nick .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}


def say(server=None, nick=None, text=None, **kwargs):
  if is_authed(nick):
    rcommand, rchannel, rmessage = split_space(text, 2)
    server.privmsg(rchannel, rmessage)
  else:
    server.privmsg(nick, BotChat.AUTH_NOT)

say.settings = {
  'events': utils.plugin.EVENTS.PRIVMSG,
  'text': r"(msg|say) .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}


def action(server=None, nick=None, text=None, **kwargs):
  if is_authed(nick):
    rcommand, rchannel, rmessage = split_space(text, 2)
    server.action(rchannel, rmessage)
  else:
    server.privmsg(nick, BotChat.AUTH_NOT)

action.settings = {
  'events': utils.plugin.EVENTS.PRIVMSG,
  'text': r"(me|action) .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}