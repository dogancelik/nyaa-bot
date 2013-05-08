import re


class TopicChat(object):
  Host = "The host for today's stream will be 4{}"
  NoHost = "No host"
  Thread = "Thread URL: {}"
  NoThread = "No thread up yet"


class TopicManager(object):
  _varregex = re.compile(r"[^:]+:\s*(.*)", re.I)
  _otherregex = re.compile("\[\s*([^\]]+)\s*\]", re.I)
  _template = {"divider": u" || ",
               "title": u"4{}",
               "time": u"3{}",
               "thread": u"8Thread Link: {}",
               "host": u"6Today's host: {}",
               "other": u"2 {}"}
  _keys = set(['title', 'time', 'thread', 'host', 'other'])

  def __init__(self):
    for key in self._keys:
      setattr(self, key, '')

  def parse(self, topic):
    first_split = map(lambda i: i.strip(), topic.split(' || ', 4))

    if len(first_split) == 5:
      self.title = first_split[0]
      self.time = first_split[1]
      self.thread = self._varregex.search(first_split[2]).groups()[0]
      self.host = self._varregex.search(first_split[3]).groups()[0]
      self.other = first_split[4]

  def set(self, item, value):
    changed = 0
    if item in self._keys:
      changed = 1
      setattr(self, item, value)
    return changed

  def _format(self, variable):
    value = getattr(self, variable)
    return self._template[variable].format(value) if len(value) > 0 else ""

  def output(self):
    return self._template["divider"].join(filter(lambda i: len(i) > 0, [
      self._format("title"),
      self._format("time"),
      self._format("thread"),
      self._format("host"),
      self._format("other")
    ])).strip()