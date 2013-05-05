# -*- coding: utf8 -*-
import itertools
import config
import re
import requests
from nyaa import page_parsers

REGEX_URI = ur"((https?://)?\w{2,}\.\w{2,4}(\.\w{2,4})?[\S]*(?<![\[\]\.\{\}]))"
COMPILED_REGEX = re.compile(REGEX_URI, re.I | re.U)


class BotChat:
  _4CHAN_OUTPUT = u"4«%s» 3«%s replies» 2«%s images»"
  YOUTUBE_OUTPUT = u"3%s by 4%s (8%s, %s views)"
  BLACK_STAR = u"★"
  WHITE_STAR = u"☆"
  PAGE_SHOUT = u"[4URL] %s"
  CONTENT_SHOUT = u"[4URL] '%s' %s"


def check_size(size):
  if size > 1048576:
    return "%s MiB" % round(size / 1048576, 2)
  else:
    return "%s KiB" % round(size / 1024, 2)


TEXT_IGNORE = ["!nk"]
NICK_IGNORE = ["Hisao-bot", "godzilla"]
WATCH_HEADERS = {'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}


def watch_url(server=None, nick=None, channel=None, text=None, sublogger=None, **kwargs):
  if nick in NICK_IGNORE or max([search in text for search in TEXT_IGNORE]):
    return

  uris = COMPILED_REGEX.findall(text)
  for uri in uris:

    try:
      new_url = uri[0]
      if uri[0].find("http:") == -1 and uri[0].find("https:") == -1:
        new_url = "http://" + uri[0]
      response = requests.get(new_url, headers=WATCH_HEADERS)
    except requests.exceptions.RequestException, e:
      sublogger.error("Error '%s' occurred on URL '%s'", str(e), uri[0])
      return

    content_type = response.headers['content-type']
    is_page = content_type.find("text") > -1

    if is_page:
      page_html = response.text
      if response.url.find("boards.4chan.org") > -1:
        parser = page_parsers._4chan_thread_parser()
        parser.feed(page_html)
        parser.close()
        page_title = BotChat._4CHAN_OUTPUT % (
          parser.quote[:60] + (u"…" if len(parser.quote) > 60 else ""), parser.reply_count, parser.image_count
        )
      elif response.url.find("youtube.com") > -1:
        parser = page_parsers.youtube_page_parser(response.text)
        if parser.is_video() is True:
          parser.parse()
          print "stars", parser.stars, 5 % parser.stars
          page_title = BotChat.YOUTUBE_OUTPUT % (
            parser.title,
            parser.uploader if parser.uploader is not False else "N/A",
            "".join([_ for _ in itertools.repeat(BotChat.BLACK_STAR, parser.stars)]) +
            "".join([_ for _ in itertools.repeat(BotChat.WHITE_STAR, 5 - parser.stars)])
            if parser.stars > 0 else "N/A",
            parser.views if parser.views is not False else "N/A"
          )

          sublogger.error(parser.title)
          sublogger.error(parser.uploader)
          sublogger.error(parser.stars)
          sublogger.error(parser.views)
        else:
          page_title = page_parsers.parse_title(response.text)
      else:
        page_title = page_parsers.parse_title(page_html)
      server.privmsg(channel, BotChat.PAGE_SHOUT % page_title)
    else:
      content_size = float(response.headers['content-length'])
      server.privmsg(channel, BotChat.CONTENT_SHOUT % (
        content_type.split(";", 1)[0],
        check_size(content_size)
      ))


watch_url.settings = {
  'events': config.EVENTS.PUBMSG,
  'text': r".*" + REGEX_URI,
  'channels': config.CHANNELS.MAIN + config.CHANNELS.DEV,
  'users': config.USERS.ALL
}