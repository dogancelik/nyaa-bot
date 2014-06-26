# -*- coding: utf-8 -*-
"""
  *NyaaTorrents search* Plugin
  ----------------------------
  Searches torrents in nyaa.eu in *English-translated Anime* category

  Usage::

    .nyaa Naruto
"""
import utils.plugin
import requests
import urllib

BOT_CHAT = "4[%s] %s (%s) %s | SE: 3%s, LE: 4%s, DL: 1%s, MSG: 2%s"
YQL_QUERY = """
select * from html where url="http://www.nyaa.se/?term=%s&cats=1_37&filter=0&sort=1&order=0" and xpath="//div[@id='main']/div[3]/table[3]/tr[contains(@class,'tlistrow')]"
"""
LOGGER_ERROR = "NyaaTorrents: %s"


class BotChat:
  NotFound = "No torrents found."
  Error = "An error occurred."


def encode_uri_component(text):
  return urllib.quote(text, safe="~()*!.'")


def nyaa(server=None, text=None, channel=None, logger=None, **kwargs):
  # First we encode the search term and put it in YQL_QUERY,
  # then requests encodes the query again otherwise it won't work
  search_term = encode_uri_component(text.split(" ", 1)[1].strip())
  query = (YQL_QUERY % search_term).strip()
  response = requests.get("http://query.yahooapis.com/v1/public/yql", params={'format': "json", 'q': query})

  error = None
  items = response.json()

  # Check for YQL related errors
  if 'error' in items:
    error = LOGGER_ERROR % items['error']['description']

  # If no results found for that query
  if items['query']['results'] is None:
    server.privmsg(channel, BotChat.NotFound)
    return

  # Just to make sure we have rows to loop through!
  try:
    items = items['query']['results']['tr']
  except Exception, e:
    error = LOGGER_ERROR % str(e)

  if error is not None:
    logger.error(error)
    server.privmsg(channel, BotChat.Error)
    return

  # YQL returns 'class' and 'td' if there is only one result
  one_item = True if 'class' in items else False
  item_count = len(items) - 1 if one_item else min(len(items), 4)

  for i in xrange(item_count):
    item = items if one_item else items[i]
    filename = item['td'][1]['a']['content']
    page_url = item['td'][1]['a']['href'].replace('www.', '')
    file_size = item['td'][3]['p']
    seeders = item['td'][4]['p']
    leechers = item['td'][5]['p']
    downloads = item['td'][6]['p']
    comments = item['td'][7]['p']

    server.privmsg(channel, BOT_CHAT % (
      str(i + 1),
      filename,
      file_size,
      page_url,
      seeders,
      leechers,
      downloads,
      comments
    ))

nyaa.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': r"\.nyaa .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}