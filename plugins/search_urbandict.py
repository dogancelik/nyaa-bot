# -*- coding: utf-8 -*-
"""
  *Urban Dictionary search* plugin
  --------------------------------

  Searches definitions in urbandictionary.com.

  Usage::

    .ud meh
    .ud5 noob
"""
import re
import utils.plugin
import json
import urllib2

API_KEY = "bc65e461224c030047116e980e9b2a63"
API_URL = "http://api.urbandictionary.com/v0/define?term=%s"

URBAN_REGEX = r"\.ud([1-5])? .*"
URBAN_CREGEX = re.compile(URBAN_REGEX, re.I)


def urban(server=None, text=None, channel=None, logger=None, **kwargs):
  word = text.split(' ', 1)[1]
  result = json.loads(urllib2.urlopen(API_URL % word).read())['list']
  for item in result[:min(len(result), int(URBAN_CREGEX.match(text).groups()[0] or 1))]:
    if len(item['definition']) > 512:  # To avoid excess flood errors
      continue
    thumbs = int(item['thumbs_up']) - int(item['thumbs_down'])
    message = u"2» " + u"2 » ".join(item['definition'].split("\n\n")) + u" " + (u"3+" if thumbs > 0 else u"4") + unicode(thumbs) + u" votes"
    server.privmsg(channel, message)

urban.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': URBAN_REGEX,
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}