# -*- coding: utf8 -*-
import config
import re
import urllib2
import HTMLParser

regexuri = ur"(https?\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?)"
curi = re.compile(regexuri, re.I | re.U)

class _4chan_thread_parser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.quote = ""
    self.quotestop = None
    self.replycount = -1
    self.imagecount = 0

  def handle_starttag(self, tag, attrs):
    if self.quotestop is None and tag == "blockquote":
      self.quotestop = False
    if tag == "blockquote":
      self.replycount += 1
    if tag == "a" and attrs[0][1] == "fileThumb":
      self.imagecount += 1

  def handle_data(self, data):
    if self.quotestop is False:
      self.quote += data + " "

  def handle_endtag(self, tag):
    if self.quotestop is False:
      self.quotestop = True
      self.quote = self.quote.strip()

  def preview_thread(self):
    return u"4«%s» 3«%s replies» 2«%s images»" % (self.quote[:60] + (u"…" if len(self.quote) > 60 else ""), self.replycount, self.imagecount)

def read_title(data):
  start = data.find("<title>")+7
  end = data.find("</title>")
  if start == -1 or end == -1:
    return None
  res = data[start:end]
  return HTMLParser.HTMLParser().unescape(res) if len(res) > 0 else None

def sizecheck(size):
  if size > 1048576:
    return "%s MiB" % round(size / 1048576, 2)
  else:
    return "%s KiB" % round(size / 1024, 2)

def watchurl(server=None, nick=None, channel=None, text=None, **kwargs):
  if (nick == "Hisao-bot" and "nyaa.eu" in text) or "!nk" in text:
    return
  
  uris = curi.findall(text)
  for uri in uris:
    response = urllib2.urlopen(uri[0])
    
    page_title = None
    content_type = response.info().getheader("Content-Type")
    is_page = True if content_type.find("text") > -1 else False
    is_unicode = True if content_type.lower().find("utf") > -1 else False
    
    set_cookie = response.info().getheader("Set-Cookie")
    end_domain = ""
    try:
      end_domain = set_cookie[-(set_cookie.index("domain=")+7):].strip()
    except:
      pass
    
    if is_page:
      page_html = unicode(response.read(), "utf8") if is_unicode else response.read()
      if end_domain.find(".4chan.org") > -1:
        parser = _4chan_thread_parser()
        parser.feed(page_html)
        parser.close()
        page_title = parser.preview_thread()
      else:
        page_title = read_title(page_html)
      server.privmsg(channel, "[4URL] %s" % page_title)
    else:
      server.privmsg(channel, "[4URL] '%s' %s" % (
        content_type.split(";", 1)[0],
        sizecheck(float(response.headers["Content-Length"]))
        )
      )

watchurl.settings = {
  'events': config.EVENTS.PUBMSG,
  'text': r".*"+regexuri,
  'channels': config.CHANNELS.ALL,
  'users': config.USERS.ALL
}