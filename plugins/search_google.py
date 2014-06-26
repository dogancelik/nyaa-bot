# -*- coding: utf-8 -*-
"""
  *Google search* Plugin
  ----------------------

  Searches Google

  Usage::

  .g Nyan cat

"""
import itertools
import utils.plugin
from google import search


def gsearch_internal(query):
  return search(query, stop=3)


def gsearch(server=None, channel=None, nick=None, text=None, **kwargs):
  command, query = text.split(" ", 1)

  for url in itertools.islice(gsearch_internal(query), 0, 3):
    server.privmsg(channel if channel.find("#") > -1 else nick, u"» %s" % url)

gsearch.settings = {
  'events': utils.plugin.EVENTS.PUBMSG + utils.plugin.EVENTS.PRIVMSG,
  'text': r'\.g(oogle)? .*',
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}