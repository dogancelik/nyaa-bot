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

    $ cp config_sample.py config.py

Then edit *config.py* as you wish.

config.py --- configuration file
................................
Config file is pretty self explanatory but I will try to explain them one by one.

.. automodule:: config_sample
   :members:

Starting nyaa-bot
-----------------

If you are running Linux:

.. code-block:: bash

    $ . nyaa-bot

If you are running Windows::

    > nyaa-bot

