"Hello World" --- writing your first plugin
-------------------------------------------
Writing a plugin is easy as pie!

Create your module
__________________
First, create a Python(``.py``) file in ``plugins`` directory. Name it whatever you want as long as it doesn't conflict with any existing package modules

Import constants
________________
All constants reside in ``utils.plugin`` module so you should import it::

    import utils.plugin

Define a function
_________________
::

    def hello_world(server=None, channel=None, nick=None, **kwargs):
      server.privmsg(channel, "Hello %s" % nick)

Finally define settings for it
______________________________
::

    hello_world.settings = {
      "events": utils.plugin.EVENTS.PUBMSG,
      "text": r'Hello$',  # don't forget $ or it will create an infinite loop
      "channels": utils.plugin.CHANNELS.DEV,
      "users": utils.plugin.USERS.ALL
    }

Now you can start your nyaa-bot and typing in ``Hello`` in any channel will trigger your ``hello_world`` function.

What is ``hello_world.settings``?
.................................
Every function(the ones that you want to trigger in IRC) must have a dictionary property named ``settings`` which contains following:

**"events" to watch:**

* ``utils.plugin.EVENT.PUBMSG``
* ``utils.plugin.EVENT.ACTION``, (``/me`` command)
* ``utils.plugin.EVENT.PRIVMSG``
* A user defined list or string (**using string is not recommend**)
* or even combine them: ``utils.plugin.EVENT.PUBMSG + utils.plugin.EVENT.PRIVMSG + ["privnotice"]``

**"channels" to watch:**

* ``utils.plugin.CHANNELS.ALL``
* A user defined list

**"users" to watch:** (``hello_world.settings['users']``)

* ``utils.plugin.USERS.ALL``
* ``utils.plugin.USERS.OP`` will grant access to Operators and up
* ``utils.plugin.USERS.HALFOP`` will grant access to Half Operators and up
* ``utils.plugin.USERS.VOICE`` will grant access to Voice users and up
* A user defined list


**"text" to watch:**

This is a RegEx string, prefix your string with ``r`` so it doesn't escape anything.::

    "text": r'^colou?r'

