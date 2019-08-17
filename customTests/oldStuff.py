import os
import sys
import psutil
import math
from random import choice


# Implementing a "memory manager" to avoid high
# memory usage that can lead to system hangs
class FillMemoryIncrementalyUntilCrash(object):

    def __init__(self):
        self.path_depths = [2, 3, 4, 5, 6]
        self.path_names = ["home", "etc", "opt", "root", "dev", "var", "usr"]
        self.proc = psutil.Process(os.getpid())
        self.paths = []
        self.max_mem_usage = self.define_max_memory_usage_until_exception()

    def define_max_memory_usage_until_exception(self):
        mem_values = dict(psutil.virtual_memory()._asdict())
        avail_digits = int(math.log10(mem_values["available"]))
        shared_digits = int(math.log10(mem_values["shared"]))
        if shared_digits < avail_digits:
            return int(mem_values["available"] - mem_values["shared"])
        else:
            return int(mem_values["free"])

    # creates a random most definitely non-existent "system" path
    # this is just used to fill the memory....
    def create_path(self, path_depth=None):
        desired_depth = path_depth or choice(self.path_depths)
        new_path = "/".join(choice(self.path_names) for i in range(desired_depth))
        # print("Created path is: /%s" % new_path)
        return ("/%s" % new_path).encode()

    def fill_memory(self, increment=2):
        avail_choices = [increment, choice(self.path_depths)]
        print("Increment is %i" % increment)
        print("Mem usage in bytes: %i" % self.proc.memory_info().rss)
        for i in range(increment):
            # Raise error when occupying more than self.max_mem_usage of memory
            if self.proc.memory_info().rss >= self.max_mem_usage:
                raise MemoryError("Exceeding %i bytes limit" % self.max_mem_usage)
            # Add even more randomness WARNING: this may generate a very big string
            # and encoding it might take a second or two more
            new_path = self.create_path(choice(avail_choices))
            # print("Adding %i bytes to memory" % sys.getsizeof(new_path))
            self.paths.append(new_path)
        if increment == 1:
            increment += increment
        else:
            increment += int(increment / 2)
        self.fill_memory(increment)

if __name__ == "__main__":
    try:
        FillMemoryIncrementalyUntilCrash().fill_memory()
    except Exception as e:
        raise e
