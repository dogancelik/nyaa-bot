import config
import re
from nyaa import pointsgame
import random

def try_parse_int(val):
  try:
    return long(val)
  except ValueError:
    return None

def parse_nickpointreason(text):
  stext = text.strip().split(" ", 3)
  if (len(stext) < 3): return False
  return [stext[1], stext[2], "" if len(stext) == 3 else stext[3]]

class BotChat(object):
  BuyItemSuccessful = "{} has bought {}!"
  BuyItemUnsuccessful = "{}: You don't have enough rupees to buy that or you already have it"
  BetWin = "{} has won the bet!!"
  BetLose = "{} has lost the bet."
  BetNotEnoughPoints = "{}: You don't have enough rupees. Go cut down some hedges or break some pots for more!"
  MultiBet = "{}: Won: {} times (3+{} rupees) - Lost: {} times (4-{} rupees) - Current: {} rupees"
  MyStats = "Rupees: {}"
  DailyLogin = "It's.. not like I wanted to give you these %s Rupees... baka!"
  Requires2People = "The player must be in the same channel as you ._."
  TransferSuccessful = "Transfer complete!"
  TransferUnsuccessful = "Not enough rupees desu~"
  StoreItem = "Item: %s | Price: %s rupee(s) | Active for: %s | To buy: .buy %s"
  TopPlayer = "#{}4 {} with2 {} rupees; "
  WelcomeDefault = "Hello {}-san!"
  Pets = "pets {}"

def buy_item(server=None, nick=None, channel=None, text=None, **kwargs):
  item_id = try_parse_int(text.split(' ', 1)[1])
  if item_id is None: return
  player = pointsgame.select_player_by_name(nick)
  ret = pointsgame.buy_item(player[0], item_id)
  if ret >= 0:
    server.privmsg(channel, BotChat.BuyItemSuccessful.format(nick, pointsgame.items[item_id]['name']))
    if ret == 4:
      server.kick(channel, nick, "KAWAII KICK!")
  else:
    server.privmsg(channel, BotChat.BuyItemUnsuccessful.format(nick))

buy_item.settings = {
  "events"   : config.EVENTS.PUBMSG,
  "text"     : r'\.buy.*',
  "channels" : config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users"    : config.USERS.ALL
}

def store(server=None, nick=None, **kwargs):
  server.notice(nick, BotChat.MyStats.format(pointsgame.select_player_by_name(nick)[2]))
  index = 0
  for item in pointsgame.items:
    server.notice(nick, BotChat.StoreItem % (item['name'], item['price'], str(item['duration']), index))
    index += 1

store.settings = dict(
  events=config.EVENTS.PUBMSG,
  text=r"\.store",
  channels=config.CHANNELS.MAIN+config.CHANNELS.DEV,
  users=config.USERS.ALL
)


def bet(server=None, nick=None, channel=None, text=None, **kwargs):
  rawpoint = text.split(' ', 1)[1]

  times = 1
  if "*" in rawpoint:
    times = try_parse_int(rawpoint.split('*', 1)[1])
    times = times if times is not None else 1

  player = pointsgame.select_player_by_name(nick)

  if rawpoint == "max":
    point = player[2]
  elif times is 1:
    point = try_parse_int(rawpoint)
  else:
    point = try_parse_int(rawpoint.split("*", 1)[0])

  if point is None or point > 100000:
    return

  last_bet = times_win = times_lose = 0
  for time in range(times):
    last_bet = pointsgame.enter_bet(player[0], point)
    if last_bet > 0:
      times_win += 1
    elif last_bet < 0:
      times_lose += 1
  
  if times > 1:
    player = pointsgame.select_player_by_name(nick)
    message = BotChat.MultiBet.format(nick, times_win, times_win*point*2, times_lose, times_lose*point, player[2])
    if times_win > times_lose:
      server.privmsg(channel, message)
    else:
      server.notice(nick, message)
  else:
    if last_bet > 0:
      server.privmsg(channel, BotChat.BetWin.format(nick))
    elif last_bet < 0:
      server.notice(nick, BotChat.BetLose.format(nick))
    elif last_bet == 0:
      server.notice(nick, BotChat.BetNotEnoughPoints.format(nick))

bet.settings = {
  "events"   : [config.EVENTS.PRIVMSG, config.EVENTS.PUBMSG],
  "text"     : r'\.bet.*',
  "channels" : config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users"    : config.USERS.ALL
}

def my_stats(server=None, nick=None, channel=None, text=None, **kwargs):
  params = text.strip().split(' ', 1)
  query_nick = params[1] if len(params) > 1 else nick 
  player = pointsgame.select_player_by_name(query_nick)
  server.privmsg(channel, BotChat.MyStats.format(player[2]))

my_stats.settings = {
  "events"   : [config.EVENTS.PRIVMSG, config.EVENTS.PUBMSG],
  "text"     : r'\.my.*',
  "channels" : config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users"    : config.USERS.ALL
}

def give(server=None, channel=None, nick=None, text=None, sublogger=None, **kwargs):
  command, user, points = text.split(' ', 2)
  old_id = pointsgame.select_player_by_name(nick)[0]
  new_id = pointsgame.select_player_by_name(user)[0]
  points = try_parse_int(points)
  if points <= 0 or server.inchannel(channel, user) is False:
    server.notice(nick, BotChat.Requires2People)
  if pointsgame.transfer_points(old_id, new_id, points):
    server.notice(nick, BotChat.TransferSuccessful)
  else:
    server.notice(nick, BotChat.TransferUnsuccessful)

give.settings = dict(
  events=config.EVENTS.PUBMSG,
  text=r"\.(give).*",
  channels=config.CHANNELS.MAIN+config.CHANNELS.DEV,
  users=config.USERS.ALL
)

def reward_punish_player(text=None, **kwargs):
  npr = parse_nickpointreason(text)
  if npr is False: return
  npr[1] = try_parse_int(npr[1])
  if npr[1] is None: return
  player = pointsgame.select_player_by_name(npr[0])
  if (text[1:7] == "reward"):
    pointsgame.reward_player(player[0], npr[1], npr[2])
  elif (text[1:7] == "punish"):
    pointsgame.punish_player(player[0], npr[1], npr[2])

reward_punish_player.settings = {
  "events"   : config.EVENTS.PUBMSG,
  "text"     : r'\.(reward|punish).*',
  "channels" : config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users"    : config.USERS.HALFOP_UP
}

def set_welcome(nick=None, text=None, **kwargs):
  if text.find(".reward") > -1 or text.find(".punish") > -1:
    return
  pointsgame.set_welcome(nick, text.split(' ', 1)[1])

set_welcome.settings = {
  'events'  : config.EVENTS.PUBMSG,
  'text'    : r'\.(sw|setwelcome).*',
  'channels': config.CHANNELS.MAIN+config.CHANNELS.DEV,
  'users'   : config.USERS.ALL
}

def register_player(nick):
  pointsgame.add_player(nick)
  player = pointsgame.select_player_by_name(nick)
  pointsgame.logger.info("User (#%s) %s registered!", player[0], nick)
  pointsgame.daily_player_check(nick)

def nick_change_check(channel=None, **kwargs):
  if pointsgame.select_player_by_name(channel) is None:
    register_player(channel)

nick_change_check.settings = dict(
  events="nick",
  text=r".*",
  channels=config.CHANNELS.MAIN + config.CHANNELS.DEV,
  users=config.USERS.ALL
)

channel_to_check = '#nyaa-nyaa'
def join_check(server=None, nick=None, channel=None, **kwargs):
  global channel_to_check
  channel_to_check = channel
  player = pointsgame.select_player_by_name(nick)

  if player is not None:
    user_id = player[0]
    if pointsgame.has_item(user_id, 1):
      server.send_raw("MODE %s +v %s" % (channel, nick))
    if pointsgame.has_item(user_id, 0):
      server.action(channel, BotChat.Pets.format(nick))
    if pointsgame.has_item(user_id, 2):
      msg = pointsgame.get_welcome(nick)
      msg = msg[1].format(nick) if msg is not None else BotChat.WelcomeDefault.format(nick)
      server.privmsg(channel, msg)

    pointsgame.daily_player_check(nick)
  else:
    register_player(nick)

join_check.settings = {
  "events"   : "join",
  "text"     : "",
  "channels" : config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users"    : config.USERS.ALL
}

user_names = []
def request_names(server=None, **kwargs):
  global user_names, channel_to_check
  user_names = []
  server.send_raw("NAMES %s" % channel_to_check)

request_names.settings = {
  "events": "ping",
  "text": r".*",
  "channels": config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users": config.USERS.ALL
}

nameregex = re.compile("[a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]*", re.I)
def get_names(text=None, **kwargs):
  global user_names
  names = text.split(":", 1)
  names = names[0] if len(names) == 1 else names[1]
  user_names.extend(nameregex.findall(names))

get_names.settings = {
  "events": "namreply",
  "text": r".*",
  "channels": config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users": config.USERS.ALL
}

def daily_login_check(server=None, **kwargs):
  pass
  """
  global user_names, channel_to_check

  def check_callback(player, points):
    if points > 0:
      server.notice(player, BotChat.DailyLogin % points)

  pointsgame.daily_all_check(user_names, check_callback)

  for user_name in user_names:
    login = pointsgame.daily_login_check(user_name)
    if login > 0:
      print login
      server.notice(user_name, BotChat.DailyLogin % (login))
  """

daily_login_check.settings = {
  "events": "endofnames",
  "text": r".*",
  "channels": config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users": config.USERS.ALL
}

def top(server=None, channel=None, **kwargs):
  top = pointsgame.get_top_players()
  rstr = ""
  for i in range(len(top)):
    rstr += BotChat.TopPlayer.format(i+1, top[i][0], top[i][1])
  server.privmsg(channel, rstr.strip())

top.settings = {
  "events": config.EVENTS.PUBMSG,
  "text": r"\.top$",
  "channels": config.CHANNELS.MAIN+config.CHANNELS.DEV,
  "users": config.USERS.ALL
}