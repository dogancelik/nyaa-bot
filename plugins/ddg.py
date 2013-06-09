# -*- coding: utf-8 -*-
"""
  *DuckDuckGo* Plugin
  -------------------
  Usage::

    .ddg How I Met Your Mother (shows 3 results)
    .ddg5 Japanese (shows 5 results)
"""
import utils.plugin
import duckduckgo
import urllib
import re

DDG_REGEX = ur"\.ddg([1-5])? .*"
DDG_CREGEX = re.compile(DDG_REGEX, re.I)


def ddg(server=None, channel=None, text=None, **kwargs):
  query = unicode(text).split(u' ', 1)[1]
  result = duckduckgo.query(query.encode("utf-8"))

  if len(result.related) > 0:
    for related in result.related[:(int(DDG_CREGEX.match(text).groups()[0] or 3))]:
      pack = related.text.split(u',', 1)
      if len(pack) == 2:
        title, info = pack
      else:
        title = pack[0]
        info = None
      server.privmsg(channel, u"2%s%s » 4%s" % (
        title,
        u", 3%s" % info if info is not None else u"",
        related.url.replace(u"duckduckgo.com", u"ddg.gg").replace(u"?kp=1", u"")
      ))
  else:
    server.privmsg(channel, u"No related definitions found. Go to http://ddg.gg/%s" % urllib.quote(query.encode("utf-8")))

ddg.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': DDG_REGEX,
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}