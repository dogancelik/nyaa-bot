from os import path
import re
import utils.plugin
import config

WATCH_CHANNEL = ["#nyaa-nyaa"]
MOTD_FILE = path.join(path.dirname(__file__), "motd.txt")


def readmotd(as_string=False):
  f = open(MOTD_FILE, "r")
  if as_string is not False:
    ret = f.read()
  else:
    ret = [line.rstrip("\r\n") for line in f]
  f.close()
  return ret


def writemotd(text):
  f = open(MOTD_FILE, "w")
  if isinstance(text, list):
    f.writelines(text)
  else:
    f.write(text)
  f.close()


def sendmotd_internal(server, nick, lines):
  for line in lines:
    server.notice(nick, line)


def setmotd(server=None, nick=None, text=None, **kwargs):
  try:
    command, query = text.split(" ", 1)
  except ValueError:
    sendmotd_internal(server, nick, readmotd())
  else:
    sed = re.match(r"s/(.*)/(.*)/(g)?", query, re.I)
    if sed is not None:
      query = readmotd(True).replace(
        sed.groups()[0],
        sed.groups()[1],
        1 if sed.groups()[2] is None else None
      )
    query = query.replace("|", "\n").strip()
    writemotd(query)
    sendmotd_internal(server, nick, readmotd())

setmotd.settings = {
  'events': utils.plugin.EVENTS.PUBMSG + utils.plugin.EVENTS.PRIVMSG,
  'text': r"\.motd( .*)?",
  'channels': WATCH_CHANNEL,
  'users': utils.plugin.USERS.HALFOP_UP
}


def sendmotd(server=None, nick=None, **kwargs):
  if not nick in config.DEV_NICKS:
    sendmotd_internal(server, nick, readmotd())

sendmotd.settings = {
  'events': "join",
  'text': r".*",
  'channels': WATCH_CHANNEL,
  'users': utils.plugin.USERS.ALL
}