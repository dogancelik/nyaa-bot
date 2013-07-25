Quick Start
===========

Installation
------------
For the time being, you can only install *nyaa-bot* locally.

To install *nyaa-bot*:

.. code-block:: bash

    $ git clone git://github.com/dogancelik/nyaa-bot.git
    $ cd nyaa-bot

There is only one dependency and that is *watchdog* for watching plugin changes.

If you use Ubuntu, you have to install *python-yaml* from the Ubuntu repository first:

.. code-block:: bash

    $ sudo apt-get install python-yaml

Then:

.. code-block:: bash

    $ pip install watchdog

.. note::

    Installing *watchdog* is required but using it is optional.

**TL;DR**: If you want to install everything, :code:`pip install -r requirements.txt`

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

