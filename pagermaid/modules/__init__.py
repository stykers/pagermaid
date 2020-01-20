""" PagerMaid module init. """

from os.path import dirname, basename, isfile
from glob import glob
from pagermaid import logs


def __list_modules():
    mod_paths = glob(dirname(__file__) + "/*.py")
    result = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]
    return result


module_list = sorted(__list_modules())
logs.info("Loading modules: %s", str(module_list))
__all__ = module_list + ["all_modules"]
