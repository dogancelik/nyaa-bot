import sqlite3
from hashlib import md5
from uuid import getnode
import random
import logging
import datetime
import os

db = sqlite3.connect(os.path.join(os.path.dirname(__file__), "pointsgame.db"), detect_types=sqlite3.PARSE_DECLTYPES,
                     check_same_thread=False)
logging.basicConfig()  # To avoid "No handlers found" error
logger = logging.getLogger("game")
logger.setLevel(logging.DEBUG)


def create_tables():
  cur = db.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, name TEXT COLLATE NOCASE, point INTEGER)")
  cur.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, user_id INTEGER, t_type INTEGER, t_point INTEGER, t_reason TEXT, t_date TIMESTAMP)")
  cur.execute("CREATE TABLE IF NOT EXISTS purchase (id INTEGER PRIMARY KEY, user_id INTEGER, item_id INTEGER, item_count INTEGER, p_start TIMESTAMP, p_end TIMESTAMP)")
  cur.execute("CREATE TABLE IF NOT EXISTS welcome (name TEXT PRIMARY KEY, message TEXT)")
  db.commit()


create_tables()


def drop_tables():
  cur = db.cursor()
  cur.execute("DROP TABLE IF EXISTS players")
  cur.execute("DROP TABLE IF EXISTS history")
  cur.execute("DROP TABLE IF EXISTS purchase")
  cur.execute("DROP TABLE IF EXISTS welcome")
  db.commit()


def add_player(name, point=0):
  if select_player_by_name(name) is not None:
    logger.error("User '%s' already exists", name)
    return False
  cur = db.cursor()
  cur.execute("INSERT INTO players VALUES(NULL, ?, ?)", (name, point))
  db.commit()
  return select_player_by_id(cur.lastrowid)


def get_special_key(id):
  hash = md5()
  hash.update(str(getnode()))
  hash.update(str(id))
  return hash.hexdigest()


def select_player_by_id(id):
  cur = db.cursor()
  cur.execute("SELECT * FROM players WHERE id=?", (id, ))
  return cur.fetchone()


def select_player_by_name(name):
  cur = db.cursor()
  cur.execute("SELECT * FROM players WHERE name=?", (name, ))
  return cur.fetchone()


def get_all_players():
  cur = db.cursor()
  cur.execute("SELECT * FROM players")
  return cur.fetchall()


def get_top_players(count=5):
  cur = db.cursor()
  cur.execute("SELECT name, point FROM players ORDER BY point DESC LIMIT " + str(count))
  return cur.fetchall()


def take_points(user_id, t_type, t_point, t_reason=''):
  t_point = abs(t_point)
  cur = db.cursor()
  cur.execute("UPDATE players SET point=point-? WHERE id=?", (t_point, user_id))
  cur.execute("INSERT INTO history VALUES(NULL, ?, ?, ?, ?, ?)",
              (user_id, t_type, -t_point, t_reason, datetime.datetime.now()))
  db.commit()


def give_points(user_id, t_type, t_point, t_reason=''):
  t_point = abs(t_point)
  cur = db.cursor()
  cur.execute("UPDATE players SET point=point+? WHERE id=?", (t_point, user_id))
  cur.execute("INSERT INTO history VALUES(NULL, ?, ?, ?, ?, ?)",
              (user_id, t_type, t_point, t_reason, datetime.datetime.now()))
  db.commit()


def transfer_points(old_id, new_id, points=0):
  old_points = select_player_by_id(old_id)[2] if points is 0 else (
    points if select_player_by_id(old_id)[2] >= points else 0)
  if old_points > 0:
    take_points(old_id, 2, old_points, "Transfer to {}".format(new_id))
    give_points(new_id, 3, old_points, "Transfer from {}".format(old_id))
    logger.info("Transfer from %s to %s completed successfully (Points sent: %s)", old_id, new_id, old_points)
    return True
  else:
    logger.info("Transfer from %s to %s failed because %s hasn't got enough points", old_id, new_id, old_id)
    return False


def enter_bet(user_id, point):
  if select_player_by_id(user_id)[2] >= point > 0:
    item_factor = 1.00
    if has_item(user_id, 4):
      used_item = use_item(user_id, 4)
      if used_item is not False:
        logger.info("User %s used an item for more win chance", user_id)
        item_factor = 0.80

    take_points(user_id, 4, point)
    a = point / random.randrange(345, 456)
    random_between = int((2 ** a + (1 if a < 1 else round(a))) * item_factor)
    if random.randrange(random_between + 1) == random_between:
      logger.info("User %s has won the bet (Points: +%s)", user_id, point * 2)
      give_points(user_id, 5, point * 3)
      return point * 2
    else:
      logger.info("User %s has lost the bet (Points: -%s)", user_id, point)
      return -point
  else:
    logger.info("User %s hasn't got enough points to bet", user_id)
    return 0


def punish_player(user_id, point, reason=''):
  take_points(user_id, 7, point, reason)
  logger.info("Punished user %s for '%s' (Points: -%s)", user_id, reason, point)


def reward_player(user_id, point, reason=''):
  give_points(user_id, 8, point, reason)
  logger.info("Rewarded user %s with %s points for '%s'", user_id, point, reason)


def add_to_purchase(user_id, item_id, item_count, start_date, end_date):
  cur = db.cursor()
  cur.execute("INSERT INTO purchase VALUES(NULL, ?, ?, ?, ?, ?)", (user_id, item_id, item_count, start_date, end_date))
  db.commit()


def get_purchase(user_id, item_id):
  cur = db.cursor()
  cur.execute("SELECT * FROM purchase WHERE user_id=? AND item_id=? ORDER BY id DESC LIMIT 1",
              (user_id, item_id))
  return cur.fetchone()


def has_item(user_id, item_id):
  datenow = datetime.datetime.now()
  purchase = get_purchase(user_id, item_id)
  if purchase is not None:
    if purchase[4] <= datenow < purchase[5]:
      logger.debug("User %s already has item %s", user_id, item_id)
      return True
    else:
      logger.debug("User %s has item %s but it's expired!", user_id, item_id)
      return False
  else:
    logger.debug("User %s doesn't have item %s", user_id, item_id)
    return False


def use_item(user_id, item_id):
  purchase = get_purchase(user_id, item_id)
  purchase_id = purchase[0]
  item_count = purchase[3]

  if item_count > 0:
    current_count = item_count - 1
    cur = db.cursor()
    cur.execute("UPDATE purchase SET item_count=? WHERE id=?", (current_count, purchase_id))
    return current_count
  else:
    return False


items = [
  dict(name="Scroll of Petting", price=50, duration=datetime.timedelta(weeks=1), count=50),
  dict(name="Ring of Voice", price=100, duration=datetime.timedelta(weeks=1), count=0),
  dict(name="Cloak of Admiration", price=200, duration=datetime.timedelta(weeks=1), count=0),
  dict(name="Scroll of Ultimate Kick", price=250, duration=datetime.timedelta(weeks=1), count=0),
  dict(name="Book of Fortunes", price=500, duration=datetime.timedelta(days=1), count=10),
  dict(name="Kick Tickets", price=3000, duration=datetime.timedelta(weeks=1), count=3)
]


def buy_item(user_id, item_id):
  date_now = datetime.datetime.now()
  try:
    item_price = items[item_id]['price']
    item_expires = date_now + items[item_id]['duration']
    item_count = items[item_id]['count']
  except ValueError:
    logger.error("Item with missing attributes (Item ID: %s)", item_id)
    return -3

  if 0 < item_price <= select_player_by_id(user_id)[2]:
    if has_item(user_id, item_id) is False:
      take_points(user_id, 6, item_price, 'Item {}'.format(item_id))
      add_to_purchase(user_id, item_id, item_count, date_now, item_expires)
      logger.info("User %s has bought item %s", user_id, item_id)
      return item_id
    else:
      logger.info("Valid item %s already exists on user %s", item_id, user_id)
      return -1
  else:
    logger.info("User %s hasn't got enough points to buy item %s", user_id, item_id)
    return -2


def last_login(user_id, not_login=False):
  cur = db.cursor()
  cur.execute("SELECT t_date, t_point FROM history WHERE user_id=? AND t_type=? ORDER BY id DESC LIMIT 1",
              (user_id, 0 if not_login is False else 1))
  ret = cur.fetchone()
  return ret if ret is not None else (None, None)


def get_welcome(name):
  cur = db.cursor()
  cur.execute("SELECT * FROM welcome WHERE name=?", (name, ))
  return cur.fetchone()


def set_welcome(name, text):
  r_text = get_welcome(name)
  if r_text is not None:
    cur = db.cursor()
    cur.execute("UPDATE welcome SET message=? WHERE name=?", (text, name))
    db.commit()
    logger.info("Player %s updated their welcome message", name)
  else:
    cur = db.cursor()
    cur.execute("INSERT INTO welcome VALUES(?, ?)", (name, text))
    db.commit()
    logger.info("Player %s created their welcome message", name)


LOGIN_BASE_POINTS = 10


def daily_all_check(current_players, player_callback):
  points = LOGIN_BASE_POINTS
  players = get_all_players()
  for player in players:
    now_date = datetime.datetime.now()
    last_date = last_login(player[0])
    last_date = last_date if last_date is not None else now_date
    future_date = last_date + datetime.timedelta(days=1)

    try:  # Logged in
      current_players.index(player[1])
      if not last_date <= now_date < future_date:
        give_points(player[0], 0, points)
        logger.info("User %s has logged in for today! (Points: +%s)", player[0], points)
        player_callback(player[1], points)
    except ValueError:  # Not logged in
      last_date = last_login(player[0], True)
      last_date = last_date if last_date is not None else now_date
      if not last_date <= now_date < future_date and player[2] >= points:
        take_points(player[0], 1, points)
        logger.info("User %s hasn't logged in for today. (Points: -%s)", player[0], points)
        player_callback(player[1], -points)


def daily_player_check(name):
  player = select_player_by_name(name)
  if player is None:
    return None
  user_id = player[0]

  last_date, last_point = last_login(user_id)
  now_date = datetime.datetime.now()
  if last_date is None:  # new user
    last_point = LOGIN_BASE_POINTS
    last_date = now_date
  future_date = last_date + datetime.timedelta(days=1)

  if not (last_date < now_date < future_date):
    yesterday = now_date - datetime.timedelta(days=1)
    if (yesterday.date() <= last_date.date() <= now_date.date()) and (last_point < 100):  # if user logged in yesterday
      last_point += 1
    give_points(user_id, 0, last_point)
    logger.info("User %s has logged in for today! (Points: +%s)", user_id, last_point)
    return last_point
  else:
    return 0


"""
  Transaction types:
  0 - Daily log-in
  1 - Daily not log-in
  2 - Transfer/Take points from (-*)
  3 - Transfer/Give points to (+*)
  4 - Enter bet (-*)
  5 - Win bet (+*)
  6 - Purchase item from shop
  7 - Punishment (-*)
  8 - Reward (+*)
"""