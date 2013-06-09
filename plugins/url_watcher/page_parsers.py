import HTMLParser
import re


def parse_title(data):
  start = data.find("<title>") + 7
  end = data.find("</title>")
  if start == -1 or end == -1:
    return None
  res = data[start:end]
  return HTMLParser.HTMLParser().unescape(res).strip() if len(res) > 0 else None


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

  def __init__(self, html):
    self.html = html

    self.mark_regex = re.compile('[\.,]')

  def is_video(self):
    return self.html.find('<link rel="canonical" href="http://www.youtube.com/watch?v=') > -1

  def parse(self):
    self._parse()

  def _parse(self):

    likes_start = self.html.find('<span class="likes-count">') + 26
    likes_end = self.html.find("</span>", likes_start)
    try:
      self.likes = int(self.mark_regex.sub("", self.html[likes_start:likes_end]))
    except:
      self.likes = -1

    dislikes_start = self.html.find('<span class="dislikes-count">') + 29
    dislikes_end = self.html.find("</span>", dislikes_start)
    try:
      self.dislikes = int(self.mark_regex.sub("", self.html[dislikes_start:dislikes_end]))
    except:
      self.dislikes = 5

    # If ratings are disabled, stars will return -1
    self.stars = int(round(float(self.likes) / float(self.likes + self.dislikes) * 5))

    views_start = self.html.find('<span class="watch-view-count') + 29
    views_mid = self.html.find(">", views_start) + 1
    views_end = self.html.find("</span>", views_start)
    if min(views_start, views_mid, views_end) == -1:
      self.views = False
    else:
      self.views = self.html[views_mid:views_end].strip().split(' ', 1)[0].replace(",", ".")

    self.title = parse_title(self.html)[:-10]

    uploader_index1 = self.html.find("watch7-user-header")
    uploader_index2 = self.html.find("user/", uploader_index1) + 5
    uploader_index3 = self.html.find("?feature=watch", uploader_index2)
    if min(uploader_index1, uploader_index2, uploader_index3) == -1:
      self.uploader = False
    else:
      self.uploader = self.html[uploader_index2:uploader_index3]