# -*- coding: utf-8 -*-
"""
  *YouTube search* plugin
  -----------------------

  Searches YouTube videos.

  .. note:: Don't forget to add `GOOGLE_API_KEY` to `config.py` for more API limit

  Usage::

    .yt nyan cat
"""

from utils import plugin
import requests
import config

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
SEARCH_PAYLOAD = {
  'part': "snippet",
  'maxResults': 4,
  'type': "video"
}
SEARCH_OUTPUT = u"4,0► {} by {} - https://youtu.be/{}"
GOOGLE_API_KEY = "GOOGLE_API_KEY"

if not hasattr(config, GOOGLE_API_KEY):
  reload(config)

if hasattr(config, GOOGLE_API_KEY):
  SEARCH_PAYLOAD['key'] = config.GOOGLE_API_KEY


def search(server=None, channel=None, text=None, **kwargs):
  payload = SEARCH_PAYLOAD.copy()
  payload['q'] = text.split(' ', 1)[1]

  req = requests.get(SEARCH_URL, params=payload)
  items = req.json()['items']

  for item in items:
    server.privmsg(channel, SEARCH_OUTPUT.format(item['snippet']['title'], item['snippet']['channelTitle'], item['id']['videoId']))

search.settings = {
  'events': plugin.EVENTS.PUBMSG,
  'text': r"\.yt .*",
  'channels': plugin.CHANNELS.ALL,
  'users': plugin.USERS.ALL
}