""" PagerMaid module init. """

from os.path import dirname, basename, isfile, exists
from os import getcwd, makedirs
from glob import glob
from pagermaid import logs


def __list_modules():
    module_paths = glob(dirname(__file__) + "/*.py")
    result = [
        basename(file)[:-3]
        for file in module_paths
        if isfile(file) and file.endswith(".py") and not file.endswith("__init__.py")
    ]
    return result


def __list_plugins():
    plugin_paths = glob(f"{getcwd()}/plugins" + "/*.py")
    if not exists(f"{getcwd()}/plugins"):
        makedirs(f"{getcwd()}/plugins")
    result = [
        basename(file)[:-3]
        for file in plugin_paths
        if isfile(file) and file.endswith(".py") and not file.endswith("__init__.py")
    ]
    return result


module_list = sorted(__list_modules())
plugin_list = sorted(__list_plugins())
logs.info("Loading modules: %s", str(module_list))
logs.info("Loading plugins: %s", str(plugin_list))
__all__ = module_list + ["module_list"]
