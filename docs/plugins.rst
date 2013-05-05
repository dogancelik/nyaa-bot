Plugins
=======
Every file in ``plugins`` directory is a plugin. Easy as that.

A plugin can hold multiple IRC commands.

Required packages for default plugins
-------------------------------------
If you are going to use the default plugins, you need to install these packages (with `pip <http://www.pip-installer.org/>`_):

* pytz - https://pypi.python.org/pypi/pytz
* python-dateutil - https://pypi.python.org/pypi/python-dateutil
* requests - https://pypi.python.org/pypi/requests

"Hello World" --- writing your first plugin
-------------------------------------------
Writing a plugin is easy as pie!

Create your module
__________________
First, create a file in ``plugins`` directory. Name it whatever you want as long as it ends with ``.py`` and doesn't conflict with any existing package modules (so don't make a file named ``gcalendar.py`` because there is already one in ``nyaa`` directory)

Import constants
________________
All constants reside in ``config`` module so you should import it::

    import config

Define a function
_________________
::

    def hello_world(server=None, channel=None, nick=None, **kwargs):
      server.privmsg(channel, "Hello %s" % nick)

Finally define settings for it
______________________________
::

    hello_world.settings = {
      "events": config.EVENTS.PUBMSG,
      "text": r'Hello$', # don't forget $ or it will create an infinite loop
      "channels": config.CHANNELS.DEV,
      "users": config.USERS.ALL
    }

Now you can start your nyaa-bot and typing in ``Hello`` in any channel will trigger your ``hello_world`` function.

What is ``hello_world.settings``?
_________________________________
Every function(the ones that you want to trigger in IRC) must have a dictionary property named ``settings`` which contains following:

* Events to watch (constant or list)
* Channels to watch (constant or list)
* Users to watch (constant or list)
* Text to watch (regex)

Accepted ``channels`` values
............................
* ``config.CHANNELS.ALL``
* ``config.CHANNELS.MAIN``
* ``config.CHANNELS.DEV``
* A user defined list

Accepted ``events`` values
..........................
``events`` is actually a list but you can use strings too (I don't recommend it though).

* ``config.EVENT.PUBMSG``
* ``config.EVENT.ACTION``, (/me command)
* ``config.EVENT.PRIVMSG``
* A user defined list or string

Accepted ``users`` values
.........................
* ``config.USERS.ALL``
* ``config.USERS.OP`` will grant access to Operators and up
* ``config.USERS.HALFOP`` will grant access to Half Operators and up
* ``config.USERS.VOICE`` will grant access to Voice users and up
* ``config.USERS.DEV``
* A user defined list

Accepted ``text`` values
........................
This is a :abbr:`RegEx (Regular Expression)` string.::

    "text": r'^colou?r'

