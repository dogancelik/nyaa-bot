from Pubnub import Pubnub
pubnubHost = Pubnub('pub-f9927ce4-f731-48de-af80-72bec032b31e', 'sub-812bd875-c227-11e1-b77e-c110ab282b12', None, False)

def pubnub(server, nick, channel, text, hostmask):
  if server.hasaccess('#nyaa-nyaa', nick):
    args = text.split(' ', 2)[1:]
    m_action, m_data = (args[0], '' if len(args) != 2 else args[1])
    if ('rave' in m_action) and (server.isop('#nyaa-nyaa', nick) is False):
      return
    print "Action: ", m_action, "Data: ", m_data
    info = pubnubHost.publish({
      'channel' : 'main',
      'message' : {
        'action': m_action,
        'data': m_data
      }
    })
    print(info)
    server.privmsg(nick, 'Message sent to main channel.')

pubnub.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.pub(nub)?.*',
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.OP
}