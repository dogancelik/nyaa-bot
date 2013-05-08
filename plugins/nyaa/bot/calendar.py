import config
from .. import gcalendar

class BotCalendarChat:
  XLeftToY = u"{1} left to 4'{0}'"
  NoStream = u"4No planned stream yet"
  NowPlaying = u"Now playing: 3'{0}'"
  FuturePlaying = u"Nothing is playing right now but {0}"

def if_pm(nick, channel):
  return channel if channel is not None else nick

def np(server=None, nick=None, channel=None, **kwargs):
  rettext = gcalendar.Calendar.nowplaying()
  if rettext is not False:
    rettext = BotCalendarChat.NowPlaying.format(rettext)
  else:
    rettext = gcalendar.Calendar.upcoming(2)
    if rettext is not False:
      rettext = BotCalendarChat.FuturePlaying.format(', '.join(BotCalendarChat.XLeftToY.format(item[0], item[1]) for item in rettext))
    else:
      rettext = BotCalendarChat.NoStream
  server.privmsg(if_pm(nick, channel), rettext)

def upc(server=None, nick=None, channel=None, **kwargs):
  rettext = gcalendar.Calendar.upcoming(2)
  if rettext is not False:
    rettext = ', '.join(BotCalendarChat.XLeftToY.format(item[0], item[1]) for item in rettext)
  else:
    rettext = BotCalendarChat.NoStream
  server.privmsg(if_pm(nick, channel), rettext)

def update(server=None, nick=None, channel=None, **kwargs):
  if server.hasaccess(channel, nick):
    gcalendar.Calendar.reset_json()
    server.notice(nick, 'Update finished.')

np.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.np$',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.ALL
}

upc.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.up$',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.ALL
}

update.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.update?$',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.HALFOP_UP
}