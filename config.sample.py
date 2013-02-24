import logging
LOGLEVEL = logging.DEBUG

NETWORK = 'irc.rizon.net'
PORT = 6667
NICK = 'Nyaa-Bot'
NAME = 'Nyaa-nyaa~'
NICKPWD = 'password'

# Constants for function settings


class USERS:
  ALL, OP_UP, HALFOP_UP, VOICE_UP, OP_ONLY, HALFOP_ONLY, VOICE_ONLY, NORMAL_ONLY = range(8)
  DEV = ['Developer1', 'Developer2']


class EVENTS:
  PUBMSG = 'pubmsg'
  ACTION = 'action'
  PRIVMSG = 'privmsg'


class CHANNELS:
  ALL = 0
  MAIN = ['#rizon', '#help']
  DEV = ['#developer']
  INIT = DEV
