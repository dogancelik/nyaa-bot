*commands* package
================
*commands* is a package that holds every IRC command you want to use in your nyaa-bot.

nyaa-bot will import all modules in this package except the modules with ``__`` prefix.

Every module in this package can hold multiple commands in it.

Required packages for default modules
-------------------------------------
If you are going to use the default modules, you need to install these packages (with `pip <http://www.pip-installer.org/>`_):

* pytz
* python-dateutil
* requests

Hello world (writing your first *commands* module)
---------------------------------------------------
Writing a *commands* module is easy.

Create your module
..................
Create a module in *commands* package and name it whatever you want but **make sure its name doesn't conflict with other modules**.

For example: in our ``nyaa`` package, we have a module named :module:`nyaa.gcalendar`, this means we can't create a module
named ``gcalendar`` in our ``commands`` package

Import constants
................
All constants reside in ``config`` module so you should import it::

    import config

...then define a function
.................
::

    def hello_world(server=None, channel=None, nick=None, **kwargs):
      server.privmsg(channel, "Hello %s" % nick)

...and finally define settings for it
......................
::

    hello_world.settings = {
      "events": config.EVENTS.PUBMSG,
      "text": r'Hello$', # don't forget $ or it will create an infinite loop
      "channels": config.CHANNELS.DEV,
      "users": config.USERS.ALL
    }

Now you can start your nyaa-bot and typing in ``Hello`` in any channel will trigger your ``hello_world`` function.

What is ``function_name.settings``?
-----------------------------------------
Every IRC function(the ones that you want to trigger in IRC chat) must have a settings property which contains following:

* Events to watch (contant or list)
* Channels to watch (constant or list)
* Users to watch (contant or list)
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

