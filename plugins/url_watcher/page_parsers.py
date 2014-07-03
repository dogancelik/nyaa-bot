# -*- coding: utf-8 -*-
import HTMLParser
import re
from bs4 import BeautifulSoup
import itertools


def parse_title(data):
  return BeautifulSoup(data).title.string.strip()


class _4chan_thread_parser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.quote = ""
    self.quote_stop = None
    self.reply_count = -1
    self.image_count = 0

  def handle_starttag(self, tag, attrs):
    if self.quote_stop is None and tag == "blockquote":
      self.quote_stop = False
    if tag == "blockquote":
      self.reply_count += 1
    if tag == "a" and attrs[0][1] == "fileThumb":
      self.image_count += 1

  def handle_data(self, data):
    if self.quote_stop is False:
      self.quote += data + " "

  def handle_endtag(self, tag):
    if self.quote_stop is False:
      self.quote_stop = True
      self.quote = self.quote.strip()


class youtube_page_parser():
  html = title = uploader = views = ""
  likes = dislikes = stars = 0

  YOUTUBE_OUTPUT = u"3%s by 4%s (8%s, %s views)"
  BLACK_STAR = u"★"
  WHITE_STAR = u"☆"

  def __init__(self, html):
    self.html = html

    self.mark_regex = re.compile('[\.,]')

  def is_video(self):
    return self.html.find('<link rel="canonical" href="http://www.youtube.com/watch?v=') > -1

  def parse(self):
    self._parse()

    return self.YOUTUBE_OUTPUT % (
      self.title,
      self.uploader if self.uploader is not False else "N/A",
      "".join([_ for _ in itertools.repeat(self.BLACK_STAR, self.stars)]) +
      "".join([_ for _ in itertools.repeat(self.WHITE_STAR, 5 - self.stars)])
      if self.stars > 0 else "N/A",
      self.views if self.views is not False else "N/A"
    )

  def _parse(self):
    html = BeautifulSoup(self.html)

    parsed_likes = html.find(class_="likes-count").string.replace(",", "")
    if parsed_likes:
      self.likes = int(parsed_likes)
    else:
      self.likes = 0

    parsed_dislikes = html.find(class_="dislikes-count").string.replace(",", "")
    if parsed_dislikes:
      self.dislikes = int(parsed_dislikes)
    else:
      self.dislikes = 0

    # If ratings are disabled, stars will return -1
    if self.likes == 0 and self.dislikes == 0:
      self.stars = -1
    else:
      self.stars = int(round(float(self.likes) / float(self.likes + self.dislikes) * 5))

    parsed_views = html.find(class_="watch-view-count")
    parsed_views.div.extract()
    parsed_views = parsed_views.string
    if parsed_views:
      self.views = parsed_views.replace(",", ".")
    else:
      self.views = False

    self.title = parse_title(self.html)[:-10]

    parsed_uploader = html.find(class_="yt-user-name").string
    if parsed_uploader:
      self.uploader = HTMLParser.HTMLParser().unescape(parsed_uploader)
    else:
      self.uploader = False