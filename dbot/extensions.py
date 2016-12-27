import types
import sys
import inspect
from . import Bot
from pprint import pprint

class Extensions(types.ModuleType):
    class BaseExtInfo:
        name = None
        short = None
        description = None

        provides = []
        requires = []

        help_group = None

        enable_func = None
        disable_func = None

    # class Extension


    def get_current_bot(self):
        # This is gonna look a bit hacky, but it will work.
        cur_frame = inspect.currentframe()

        for frame in inspect.getouterframes(cur_frame):
            try:
                self_arg = inspect.getargvalues(frame.frame).locals["self"]
                if isinstance(self_arg, Bot):
                    bot = self_arg
                    break
            except:
                pass
        else:
            raise Exception("Could not find context")
        return bot

    @property
    def bot(self):
        return self.get_current_bot()


# Overwrite this modules with the instanced class
sys.modules[__name__] = Extensions(__name__)
