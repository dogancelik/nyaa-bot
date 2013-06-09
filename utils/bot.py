"""
  Utils for bot
"""
import copy
import importlib
import logging
import os
import re
import sys
import types
import watchdog.events
import watchdog.observers

# TODO: Logger texts


def get_app_path():
  """
    Returns an absolute path of running process
  """
  return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_dir_path(file, no_abs=False):
  """
    Use this in plugins as: get_plugin_path(__file__)
  """
  if no_abs is True:
    return os.path.dirname(file)
  return os.path.dirname(os.path.abspath(file))


def get_basename(filename_with_ext):
  """
    Use this if you want to subtract extension from filename
  """
  return os.path.basename(filename_with_ext).rsplit(".")[0]


def get_python_name(file):
  """
    A variation of get_basename for Python files
  """
  return os.path.basename(file)[:-3]


def get_rel_path(base, target):
  """
    Returns relative path from a base path with a given target path
  """
  return os.path.relpath(target, base)


def get_module_path(basename, relative_path):
  """
    A simple trick to convert file path to module name for importing it
  """
  return re.sub(r"[\\/]", ".", relative_path) + "." + basename


class PyHandler(watchdog.events.FileSystemEventHandler):
  """
    PyHandler is meant to be only used by bot for reloading plugins.

    Handles file system events.
  """

  def __init__(self, bot_instance):
    super(PyHandler, self).__init__()
    self.bot_instance = bot_instance

  def remove_module(self, module_path, filename):
    self.bot_instance.loader.remove_module(module_path)

  def add_module(self, module_path, filename):
    self.bot_instance.loader.add_module(module_path, filename)
    self.bot_instance.loader.load_handlers(self.bot_instance.plugins[module_path])

  def reload_folder(self, src, dest):
    pass  # Not implemented

  def on_any_event(self, event):
    if os.path.isdir(event.src_path) is False:  # watchdog is buggy
      filename = os.path.basename(event.src_path)
      if filename.endswith(".py") and not filename.startswith("__"):
        module_path = ModuleLoader.get_module_path(event.src_path, self.bot_instance.app_path)
        if event.event_type == "moved" or event.event_type == "deleted":
          self.remove_module(module_path, filename)
        elif event.event_type == "modified":
          self.add_module(module_path, filename)
    else:
      if event.event_type == "moved":
        self.reload_folder(event.src_path, event.dest_path)


class PyWatcher(watchdog.observers.Observer):
  """
    PyWatcher is meant to be only used by bot for reloading plugins.

    Watches for file changes in filesystem.
  """

  def __init__(self, event_handler, path):
    super(PyWatcher, self).__init__()
    self.schedule(event_handler, path=path, recursive=True)


class Logger(logging.RootLogger):

  def __init__(self, level):
    super(Logger, self).__init__(level)

    self.file_handler = logging.FileHandler("error.log")
    self.file_handler.setLevel(logging.ERROR)
    self.addHandler(self.file_handler)

    self.stream_handler = logging.StreamHandler()
    self.addHandler(self.stream_handler)

    self.formatter = logging.Formatter("%(asctime)s %(name)-8s %(levelname)-8s %(message)s", "%m-%d %H:%M")
    self.file_handler.setFormatter(self.formatter)
    self.stream_handler.setFormatter(self.formatter)


class ModuleLoader():

  def __init__(self, bot_instance):
    self.bot_instance = bot_instance

  def load_handlers(self, module):
    """
      Loads functions with ``settings`` attribute in a module
    """
    loaded_handlers = []
    self.bot_instance.logger.debug("Inspecting module for handlers: %s", module.__name__)
    for function_name in dir(module):
      function = getattr(module, function_name)
      if type(function) == types.FunctionType:
        try:
          settings = getattr(function, "settings")
        except AttributeError:
          pass
        else:
          self.bot_instance.handlers.append(
            (re.compile(settings["text"], re.I | re.U),
            function,
            settings["events"],
            settings["channels"],
            settings["users"]),
          )
          loaded_handlers.append(function_name)
    if loaded_handlers:
      self.bot_instance.logger.debug("Loaded handlers: %s" % ', '.join(loaded_handlers))

  def remove_all_modules(self):
    self.bot_instance.handlers = []
    for plugin in copy.copy(self.bot_instance.plugins):
      try:
        self.bot_instance.logger.debug("Reloading module: %s", plugin)
        del sys.modules[plugin]
      except Exception, e:
        self.bot_instance.logger.error("Error '%s' while reloading module '%s'", str(e), plugin)
      else:
        self.bot_instance.logger.info("Reloaded module: %s", plugin)
    self.bot_instance.plugins = {}

  def add_all_modules(self, reload_modules):
    main_path = self.bot_instance.app_path
    for (paths, dirs, files) in os.walk(os.path.join(main_path, self.bot_instance.PLUGINS_DIR)):
      files = [f for f in files if f.lower().endswith(".py") and not f.startswith("__")]
      abs_path = paths  # because we use os.path.join(main_path, self.PLUGINS_DIR) in walk
      rel_path = get_rel_path(main_path, abs_path)
      self.bot_instance.logger.debug("Current dir: %s", abs_path)
      self.bot_instance.logger.debug("Found modules: %s", files)
      for filename in files:
        module_name = get_python_name(filename)
        module_path = get_module_path(module_name, rel_path)
        module_error = self.add_module(module_path, filename)
        if module_error is not None:
          if reload_modules:
            raise module_error
          sys.exit(1)

    for plugin in self.bot_instance.plugins:
      self.load_handlers(self.bot_instance.plugins[plugin])

  @staticmethod
  def get_module_path(file_path, app_path):
    return get_module_path(get_python_name(file_path), get_rel_path(app_path, get_dir_path(file_path, True)))

  def remove_module(self, module_path):
    try:
      new_handlers = []
      for handler in self.bot_instance.handlers:
        if handler[1].func_globals['__name__'] != module_path:  # import all handlers that isn't from "module"
          new_handlers.append(handler)
      self.bot_instance.handlers = new_handlers

      del self.bot_instance.plugins[module_path]
      del sys.modules[module_path]
    except Exception, e:
      self.bot_instance.logger.error("Error '%s' while removing module '%s'", str(e), module_path)
    else:
      self.bot_instance.logger.debug("Removed module: %s", module_path)

  def add_module(self, module_path, filename):
    self.bot_instance.logger.debug("Loading module: %s", filename)
    try:
      self.bot_instance.plugins[module_path] = importlib.import_module(module_path)
    except Exception, e:
      self.bot_instance.logger.error("Error in module (%s): %s", module_path, str(e))
      return e
    else:
      self.bot_instance.logger.info("Imported module: %s", module_path)
      return None