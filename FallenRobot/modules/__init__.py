from FallenRobot import LOAD, LOGGER, NO_LOAD
import glob
from os.path import basename, dirname, isfile


def __list_all_modules():
    """
    Function to list all available modules and determine which ones to load
    based on the LOAD and NO_LOAD conditions.
    """
    # Generate a list of module paths in the current directory.
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

    # If there's a LOAD condition, validate the modules specified.
    if LOAD:
        to_load = LOAD
        invalid_modules = [mod for mod in to_load if mod not in all_modules]
        if invalid_modules:
            LOGGER.error("Invalid loadorder names: %s. Quitting...", ", ".join(invalid_modules))
            quit(1)

        # Remove already loaded modules and prioritize loading the modules specified in LOAD.
        all_modules = sorted(set(all_modules) - set(to_load))
        to_load = list(all_modules) + to_load
    else:
        to_load = all_modules

    # If NO_LOAD is set, exclude the modules specified from the loading list.
    if NO_LOAD:
        LOGGER.info("Not loading: %s", ", ".join(NO_LOAD))
        to_load = [item for item in to_load if item not in NO_LOAD]

    return to_load


ALL_MODULES = __list_all_modules()
LOGGER.info("Modules to load: %s", str(ALL_MODULES))
__all__ = ALL_MODULES + ["ALL_MODULES"]
