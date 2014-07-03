# -*- coding: utf8 -*-
"""
  *URL Watcher* Plugin
  --------------------
  Watches HTTP/S URLs and gives detailed info when URLs are from YouTube or 4chan. Otherwise if it's a page, it shows the page title;
  if it's a binary file, shows file size and file type.

  Bot ignores URLs when message has ``!nk`` in it
"""
import utils.plugin
import re
import requests
import page_parsers

REGEX_URI = ur"([a-z]([a-z]|\d|\+|-|\.)*):(\/\/(((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?((\[(|(v[\da-f]{1,}\.(([a-z]|\d|-|\.|_|~)|[!\$&'\(\)\*\+,;=]|:)+))\])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=])*)(:\d*)?)(\/(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*|(\/((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)|((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)|((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)){0})(\?((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\xE000-\xF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\x00A0-\xD7FF\xF900-\xFDCF\xFDF0-\xFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?"  # @scottgonzales
COMPILED_REGEX = re.compile(REGEX_URI, re.I | re.U)


class BotChat:
  _4CHAN_OUTPUT = u"4«%s» 3«%s replies» 2«%s images»"
  PAGE_SHOUT = u"[4URL] %s"
  CONTENT_SHOUT = u"[4URL] '%s' %s"


def check_size(size):
  if size > 1048576:
    return "%s MiB" % round(size / 1048576, 2)
  else:
    return "%s KiB" % round(size / 1024, 2)


TEXT_IGNORE = ["!nk"]
NICK_IGNORE = ["Hisao-bot", "godzilla"]
HEADER_IGNORE = ["image"]
WATCH_HEADERS = {
  'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
}


def watch_url(server=None, nick=None, channel=None, text=None, logger=None, **kwargs):
  if nick in NICK_IGNORE or max([search in text for search in TEXT_IGNORE]):
    return

  uris = COMPILED_REGEX.findall(text)
  for uri in uris:
    try:
      new_url = uri[0] + ":" + uri[2]
      response = requests.head(new_url, allow_redirects=True, headers=WATCH_HEADERS)
      content_type = response.headers['content-type']
      encode_to = None
      if content_type.find("charset") == -1:
        encode_to = "utf-8"
    except requests.exceptions.RequestException, e:
      logger.error("Error '%s' occurred on URL '%s'", str(e), uri[0])
      return

    if max([search in content_type for search in HEADER_IGNORE]):
      return

    is_page = content_type.find("text") > -1

    if is_page:
      response = requests.get(new_url, headers=WATCH_HEADERS)
      if encode_to is not None:
        response.encoding = encode_to  # for sites without Content-Type(charset) header

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
          page_title = parser.parse()
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
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': r".*" + REGEX_URI,
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}