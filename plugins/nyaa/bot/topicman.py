import config
from .. import topicmanager

topicman = topicmanager.TopicManager()


def topic(server=None, nick=None, channel=None, text=None, **kwargs):
  if server.hasaccess(channel, nick):
    topicman.parse(server.get_topic(channel))
    allvars = filter(lambda i: len(i) > 0, text.split(' ', 1)[1].strip().split(';'))
    changed = 0
    for var in allvars:
      split = filter(lambda i: len(i) > 0, var.strip().split(' ', 1))
      if len(split) > 1:
        key = split[0].lower().strip()
        val = split[1]
        changed += topicman.set(key, val)
    if changed > 0:
      server.topic(channel, topicman.output())


def topicsingle(server=None, nick=None, channel=None, text=None, **kwargs):
  split = [a for a in text.split(' ', 1) if a]
  topicman.parse(server.get_topic(channel))
  command = split[0].lower().strip()[1:]
  if len(split) > 1:
    command_val = split[1].strip()
    if server.hasaccess(channel, nick):
      changed = topicman.set(command, command_val if command_val != 'delete' else '')
      if changed is True:
        server.topic(channel, topicman.output())
        server.notice(nick, "{} changed".format(command).capitalize())
  else:
    if command == 'host':
      msg = topicmanager.TopicChat.Host
      if not topicman.host or topicman.host.lower() == 'n/a':
        msg = topicmanager.TopicChat.NoHost
      server.privmsg(channel, msg.format(topicman.host))
    elif command == 'thread':
      msg = topicmanager.TopicChat.Thread
      if not topicman.thread or topicman.thread.lower() == 'n/a':
        msg = topicmanager.TopicChat.NoThread
      server.privmsg(channel, msg.format(topicman.thread))


topic.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.topic.*',
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}

topicsingle.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.(thread|host).*',
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.ALL
}