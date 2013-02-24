import config

import pusher
pusher.app_id = '26682'
pusher.key = 'b6cba2f7423272176ca6'
pusher.secret = 'f30490e440b04b608999'
p = pusher.Pusher()

def pusher(server, nick, channel, text, hostmask):
  if server.hasaccess('#nyaa-nyaa', nick):
    args = text.split(' ', 2)[1:]
    m_action, m_data = (args[0], '' if len(args) != 2 else args[1])
    if ('rave' in m_action) and (server.isop('#nyaa-nyaa', nick) is False):
      return
    print "Action: ", m_action, "Data: ", m_data
    info = p['main'].trigger('action', { 'action': m_action, 'data': m_data })
    print(info)
    server.notice(nick, 'Message sent to main channel.')

pusher.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r'\.push(er)?.*',
  "channels": config.CHANNELS.MAIN,
  "users": config.USERS.OP
}