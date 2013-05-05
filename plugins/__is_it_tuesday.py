import config
import pytz
import datetime

def is_it_tuesday(server, nick, channel, text, hostmask):
  if datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).strftime('%w') == '2':
    server.send_raw("MODE %s +v %s" % (channel, nick))

is_it_tuesday.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'.*is it (tuesday|lesbians?).*',
  "channels": config.CHANNELS.ALL,
  "users": config.USERS.ALL
}