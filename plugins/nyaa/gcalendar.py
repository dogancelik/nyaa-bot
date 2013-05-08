import urllib2
import time
import os
import json
import dateutil.parser
from datetime import datetime, tzinfo, timedelta
import pytz

class Calendar:
  _json_path = os.path.join(os.path.dirname(__file__), 'calendar.json')

  @staticmethod
  def download_json():
    url = 'https://www.googleapis.com/calendar/v3/calendars/opcqa50eg3clgcl00n2l9ral1k%40group.calendar.google.com/events?key=AIzaSyDtVqLW-hhFqVPGBtYI7rVvaN_H58JhGl0'
    file = open(Calendar._json_path, 'w')
    file.write(urllib2.urlopen(url).read())
    file.close()

  @staticmethod
  def save_json():
    if os.path.exists(Calendar._json_path):
      if time.time() - os.path.getmtime(Calendar._json_path) > 3600:
        Calendar.download_json()
    else:
      Calendar.download_json()

  @staticmethod
  def reset_json():
    os.remove(Calendar._json_path)
    Calendar.save_json()

  @staticmethod
  def load_json():
    Calendar.save_json()
    return json.loads(open(Calendar._json_path, 'r').read())

  @staticmethod
  def upcoming(count = 1):
    json = Calendar.load_json()
    edts = map(getstartseconds, json['items'])
    # firstmin = edts.index(posmin(edts))
    minsindex = map(lambda i: edts.index(i), sorted(filter(lambda x: x >= 0, edts))[:count])
    if len(minsindex) == 0:
      return False
    # startsec = mindt
    # nowsec = int(datetime.utcnow().strftime("%s"))
    # left = str(timedelta(seconds=edts[index])) # time.strftime('%H:%M:%S', time.gmtime(edts[index]))
    ret = list()
    for i in range(min(count, len(minsindex))):
      index = minsindex[i]
      time = edts[index]
      event = json['items'][index]
      left = TimeFormatter.formatlong(int(time))
      ret.append((event['summary'], left))
    return ret

  @staticmethod
  def nowplaying():
    edts = map(getseconds, Calendar.load_json()['items'])
    found = False

    for i, v in enumerate(edts):
      if (v['now'] > v['start'] and v['now'] < v['end']):
        found = v

    return found['title'] if found is not False else False


class TimeFormatter:
  @staticmethod
  def format_output(value, unit):
    if value == 0:
      return ""
    singular_output = str(value) + " " + unit
    if value == 1:
      return singular_output
    elif value > 1:
      return singular_output + "s"

  @staticmethod
  def formathours(sec):
    hours   = sec // 3600 # 60
    minutes = sec % 3600
    result = TimeFormatter.format_output(hours, "hour") + " " + TimeFormatter.format_output(minutes, "minute")
    return result.strip()

  @staticmethod
  def formatlong(value, outsec = False):
    difference = value # int(time.time()) - value
    year, month = divmod(difference, 31557600)
    month, week = divmod(month, 2629800)
    week, day = divmod(week, 604800)
    day, hour = divmod(day, 86400)
    hour, minute = divmod(hour, 3600)
    minute, second = divmod(minute, 60)
    result = ''
    if year: result += TimeFormatter.format_output(year, "year")
    if month: result += " "+TimeFormatter.format_output(month, "month")
    if week: result += " "+TimeFormatter.format_output(week, "week")
    if day: result += " "+TimeFormatter.format_output(day, "day")
    if hour: result += " "+TimeFormatter.format_output(hour, "hour")
    if minute: result += " "+TimeFormatter.format_output(minute, "minute")
    if (second > 0) and (outsec == True): result += " "+TimeFormatter.format_output(second, "second")
    return result.strip()


def getutcnow():
  return datetime.utcnow().replace(tzinfo=pytz.UTC)


def get_timezone(sub_item):
  return sub_item['timeZone'] if 'timeZone' in sub_item else 'America/Chicago'


def get_datetime(sub_item):
  return sub_item.get('dateTime') or sub_item.get('date')


def convert2utc(sub_item):
  return dateutil.parser.parse(get_datetime(sub_item)).replace(tzinfo=pytz.timezone(get_timezone(sub_item))).astimezone(pytz.utc)


def getseconds(item):
  return {
    'now': time.mktime(getutcnow().timetuple()), # it was strftime(%s) but win32 no support
    'start': time.mktime(convert2utc(item['start']).timetuple()),
    'end': time.mktime(convert2utc(item['end']).timetuple()),
    'title': item['summary']
  }


def posmin(seq):
  tempmin = float('inf')
  for val in seq:
    tempmin = min(tempmin, float('inf') if val < 0 else val)
  return tempmin


def getstartseconds(item):
  return time.mktime(convert2utc(item['start']).timetuple()) - time.mktime(getutcnow().timetuple()) # int(startutc.strftime("%s"))

"""
  Calendar ID:
  opcqa50eg3clgcl00n2l9ral1k@group.calendar.google.com

  Widget URL:
  https://www.google.com/calendar/embed?src=opcqa50eg3clgcl00n2l9ral1k@group.calendar.google.com&bgcolor=%23e6e6e6&ctz=America/New_York

  Google Key:
  https://www.googleapis.com/calendar/v3/calendars/opcqa50eg3clgcl00n2l9ral1k%40group.calendar.google.com/events?key=AIzaSyCFj15TpkchL4OUhLD1Q2zgxQnMb7v3XaM

  User Key:
  https://www.googleapis.com/calendar/v3/calendars/opcqa50eg3clgcl00n2l9ral1k%40group.calendar.google.com/events?key=AIzaSyDtVqLW-hhFqVPGBtYI7rVvaN_H58JhGl0

  Extra Args:
  &orderBy=startTime&singleEvents=true

  XML feed:
  http://www.google.com/calendar/feeds/opcqa50eg3clgcl00n2l9ral1k%40group.calendar.google.com/public/basic?orderby=starttime&futureevents=true&max-results=1&sortorder=a
"""