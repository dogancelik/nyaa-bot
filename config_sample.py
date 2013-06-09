import logging
LOG_LEVEL = logging.DEBUG
"""
**LOG_LEVEL** is the option for logging level. You can set ``LOG_LEVEL`` to these:
``logging.DEBUG``, ``logging.INFO``, ``logging.WARNING``, ``logging.ERROR``, ``logging.CRITICAL``

Using ``logging.DEBUG`` will inform you about everything, using ``logging.INFO`` won't tell you much...
"""

#: **NETWORK** is the IRC server you want to connect,
NETWORK = 'irc.rizon.net'

#: **PORT** is the port number of the server.
PORT = 6667

#: If you want to use SSL, set **USE_SSL** to ``True`` else ``False``.
USE_SSL = False

#: Your nick
NICK = 'Nyaa-Bot'

#: Your **NICK** and **NAME** will look like this on the server: *Nyaa-Bot!Nyaa@...*
NAME = 'Nyaa'

NICKPWD = 'password'
"""
If you set a password for **NICKPWD**: when you connect to the IRC server, *nyaa-bot* will send an *IDENTIFY* command to
*NickServ*. Leave it empty (``NICKPWD = ''``) if you don't want *nyaa-bot* to send a private message to *NickServ*.
"""

#: **CHANNELS** is a list for the channels you want to join when you connect to the IRC server.
CHANNELS = ["#your-channel"]

WATCH_PLUGINS = False
"""
If you set **WATCH_PLUGINS** to ``True``, the bot will watch for file changes in the plugins directory and reload
the changed files.
"""

HIDE_LOGS = []
"""
**HIDE_LOGS** This setting will hide unnecessary logs about stuff. Only available option is "unused_handlers". If you
use "unused_handlers", the bot will hide unused handlers when executing a handler.
"""

SKIP_EVENTS = []
"""
The events specified in **SKIP_EVENTS** will never get processed and plugins will not work on them. Such events as
"motd", "welcome" could be specified for clean output.
"""