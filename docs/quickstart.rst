Quick Start
===========

Installation
------------
For the time being, you can only install nyaa-bot locally.

To install nyaa-bot:

.. code-block:: bash

    $ git clone git://github.com/dogancelik/nyaa-bot.git
    $ cd nyaa-bot

Configuration
-------------
You can configure your *nyaa-bot* with *config.py* in the root directory.

There is a sample configuration file in the directory, so we copy that:

.. code-block:: bash

    $ cp config.sample.py config.py

Then edit *config.py* as you wish.

config.py --- configuration file
................................
Each variable with their explanations:

::

    import logging
    LOGLEVEL = logging.DEBUG # Logging level

    NETWORK = 'irc.rizon.net' # IRC server you want to connect to
    PORT = 6667 # Server port
    NICK = 'Nyaa-Bot' # Nick
    NAME = 'Nyaa~' # Name
    NICKPWD = 'Nyan' # Identify for NickServ

Starting nyaa-bot
-----------------

If you are running Linux:

.. code-block:: bash

    $ . nyaa-bot

If you are running Windows::

    > nyaa-bot

