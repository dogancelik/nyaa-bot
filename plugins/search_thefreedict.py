# -*- coding: utf-8 -*-
"""
  *The Free Dictionary search* Plugin
  -----------------------------------

  Searches definitions in thefreedictionary.com.

  Usage::

    .d hello

  Install notes
  _____________
  You need :term:`lxml` to use this plugin:

  Ubuntu (Linux)::

    apt-get install libxml2-dev libxslt-dev
    pip install lxml
"""
import re
import utils.plugin
from pyquery import PyQuery as pq

WORD_URL = "http://www.thefreedictionary.com/{}"


def lookup_word_internal(word):
  return pq(WORD_URL.format(word))


def lookup_word(server=None, nick=None, text=None, **kwargs):
  command, query = text.split(" ", 1)

  doc = lookup_word_internal(query)
  defs = doc("#MainTxt .pseg")

  for df in defs:
    desc = pq(df.find("i")).text()
    defi = pq(df).remove("i")
    if len(pq(defi).find(".ds-list")) == 0:
      defi = defi.text()
    else:
      i = 0
      limit = 3
      gen = defi.items(".ds-list")
      defi = u""
      for g in gen:
        if i == limit:
          break
        defi += re.sub(ur"^([0-9]+\.)", ur"2\1", g.text(), 1) + (u" " if i == limit - 1 else u" • ")
        i += 1
      defi = defi.strip()

    server.notice(nick, u"» %s %s" % (desc, defi))

  if len(defs) == 0:
    server.notice(nick, u"No definitions found for '%s'." % query)

lookup_word.settings = {
  'events': utils.plugin.EVENTS.PUBMSG + utils.plugin.EVENTS.PRIVMSG,
  'text': r'\.d(n|m)? .*',
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}