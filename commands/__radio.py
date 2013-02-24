import urllib2
import json
import config

URL_KILL = ""
URL_NPR = ""

def read_url(url):
  wurl = urllib2.urlopen(url)
  return wurl.read()

def kill(server, nick, channel, text, hostmask):
  read_url(URL_KILL)
  server.notice(nick, 'Connect after song ends.')

def npr(server, nick, channel, text, hostmask):
  jsonobj = json.loads(read_url(URL_NPR))
  server.privmsg(channel, 'Now playing in radio: ' + jsonobj['track'] + ' by ' + (jsonobj['artist'] if jsonobj['artist'] != '' else 'N/A'))

kill.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.kill$',
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.HALFOP_UP
}

npr.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.npr$',
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}