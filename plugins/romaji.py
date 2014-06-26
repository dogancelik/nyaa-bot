# -*- coding: utf-8 -*-
"""
  *Romaji* (Translation/Transliteration) Plugin
  ---------------------------------------------
  This plugin can both translate and transliterate a Japanese word or sentence to English vice versa.

  This plugin uses Bing API.

  Usage::

    .je こんにちは (Japanese to English)
    .ej Hello (English to Japanese)
    .re nihongo (Romaji to English - definition only)
    .rj nihongo (Romaji to Japanese - definition only)

  Chaining
  ________

  You can chain commands like this::

    .rje doumo (Romaji to Japanese to English)
    .jejej ごめんなさい (Jap to Eng to Jap to Eng to Jap...)

  Other languages
  _______________

  They need love too, right?::

    .tr en de Hello World (English to German)
    .tr tr en Merhaba Dünya (Turkish to English)

"""
import utils.plugin
import re
import requests
from types import BooleanType

ROMAJI_URL = 'http://romaji.org/'
ROMAJI_DISPLAY = '<!-- ROMAJI.ORG DISPLAY RESULT AREA -->'
ROMAJI_PARAMS = { 'save': 'save convert text to Romaji', 'text': '' }
ROMAJI_SAID = u"{}: '{}'"


def romaji_internal(text):
  ROMAJI_PARAMS['text'] = text.encode('shift-jis')
  req = requests.post(ROMAJI_URL, params=ROMAJI_PARAMS)
  start = req.text.index(ROMAJI_DISPLAY)
  end = req.text.rindex(ROMAJI_DISPLAY)
  fstr = req.text[start:end]
  first = fstr.index('<font color="red">')
  last = fstr.rindex('</font>')
  return re.sub('<[^<]+?>', '', fstr[first:last]).strip()


def romaji(server=None, nick=None, channel=None, text=None, **kwargs):
  if "!nk" in text:
    return
  realtext = text.split(' ',1)[1] if ".r " in text else text
  server.privmsg(channel, ROMAJI_SAID.format(nick, romaji_internal(realtext)))

# ur"(\.r\s.*|.*[\u3040-\u30FF\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A\u2E80-\u2FD5\uFF5F-\uFF9F\u3000-\u303F\u31F0-\u31FF\u3220-\u3243\u3280-\u337F\uFF01-\uFF5E].*|[\u3040-\u30FF\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A\u2E80-\u2FD5\uFF5F-\uFF9F\u3000-\u303F\u31F0-\u31FF\u3220-\u3243\u3280-\u337F\uFF01-\uFF5E].*)",
TR_URL = u"http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from={}&to={}&appId=1369A68D3D83D36A0CF025458F3AD678B4FF33BF"
J2E_URL = u"http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from=ja&to=en&appId=1369A68D3D83D36A0CF025458F3AD678B4FF33BF"
E2J_URL = u"http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from=en&to=ja&appId=1369A68D3D83D36A0CF025458F3AD678B4FF33BF"
JE_START = u'<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">'
JE_END = u'</string>'


def translate_internal(tr_from, tr_to, text):
  req = requests.get(TR_URL.format(text, tr_from, tr_to))
  try:
    start = req.text.index(JE_START) + len(JE_START)
    end = req.text.index(JE_END)
  except Exception, e:
    raise e
  return req.text[start:end]


def translate(server=None, nick=None, channel=None, text=None, **kwargs):
  command, tr_from, tr_to, q_text = text.split(" ", 3)
  tr_text = translate_internal(tr_from.upper(), tr_to.upper(), q_text)
  server.privmsg(channel, ROMAJI_SAID.format(nick, tr_text))

JISHO_URL = "http://jisho.org/words?jap={}&eng={}&dict=edict&common=on"
KANJI_MATCH = '<span class="kanji" style="z-index: 149999;">'
KANA_MATCH = '<span class="match">'
KANJI_MATCH_END = "</span>"
ENG_MATCH = '<td class="meanings_column">'
ENG_MATCH_END = '</td>'


def jisho_internal(word, english=False):
  req = requests.get(JISHO_URL.format(word, "") if english is False else JISHO_URL.format("", word))
  # English
  start = req.text.index(ENG_MATCH) + len(ENG_MATCH)
  end = req.text.index(ENG_MATCH_END, start)
  english_def = re.sub('<[^<]+?>', '', req.text[start:end]).strip()
    
  # Kanji or kana
  start = req.text.index(KANJI_MATCH) + len(KANJI_MATCH)
  end = req.text.index(KANJI_MATCH_END, start)
  if req.text[start:end].strip() == "":
    start = req.text.index(KANA_MATCH) + len(KANA_MATCH)
    end = req.text.index(KANJI_MATCH_END, start)
  kana_def = req.text[start:end].strip()

  return english_def, kana_def


def jptranslate_internal(to_en, text):
  j2e = True if to_en == "e" else False
  if j2e:
    tr_text = translate_internal("ja", "en", text)
  else:
    tr_text = translate_internal("en", "ja", text)
  return tr_text


CHAIN_CHAT = u"» ({}) ({}) {color}'{}'"
CHAIN_REGEX = r"\.([jre]{2,10}) (.*)"


def chain_translate(server=None, channel=None, text=None, **kwargs):
  command, query = re.compile(CHAIN_REGEX, re.I).match(text).groups()
  command = "".join([char.lower() for char in command])
  first_char, other_chars = command[:1], command[1:]
  last_char = first_char

  output = [(last_char, query)]
  server.privmsg(channel, CHAIN_CHAT.format(
      1,
      output[-1][0],
      output[-1][1],
      color=2
  ))
  for index, char in enumerate(other_chars):
    if char == last_char: continue
    if last_char == 'j' and char == 'r':
      output.append((char, romaji_internal(output[-1][1])))
    elif last_char == 'r' and char == 'e':
      output.append((char, jisho_internal(output[-1][1])[0]))
    elif last_char == 'r' and char == 'j':
      output.append((char, jisho_internal(output[-1][1])[1]))
    elif char == 'e' or char == 'j':
      output.append((char, jptranslate_internal(char, output[-1][1])))
    last_char = char
    server.privmsg(channel, CHAIN_CHAT.format(
      index + 2,
      output[-1][0],
      output[-1][1],
      color=3
    ))

translate.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': r"\.tr .*",
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}

romaji.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': r'\.r .*',
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}

chain_translate.settings = {
  'events': utils.plugin.EVENTS.PUBMSG,
  'text': CHAIN_REGEX,
  'channels': utils.plugin.CHANNELS.ALL,
  'users': utils.plugin.USERS.ALL
}