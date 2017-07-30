#
#   Random helpers
#
from __future__ import print_function

class vprint(object):
    verbose = False
    def __init__(self, verbosity):
        self.verbose = verbosity
        return

    def print(self,*args):
        if self.verbose: 
            print(*args)
        return
    
class dictlist(object):
    """ A dictionary containing a list for each value """

    def __init__(self):
        self.dict = {} # Do I need a getter??
        return

    def add(self, inx, val):
        """ Add a new value to the dictlist. """
        try:
            if val in self.dict[inx]:
                return # already have it
            self.dict[inx].append(val)
        except KeyError:
            # No key found, so add a new list
            self.dict[inx] = [ val ]

####
if __name__ == "__main__":
    v = vprint(True)
    v.print("This", "is", 4, "test")
    
    d = dictlist()
    d.add(1,"hi 1")
    d.add(1,"hi 2")
    d.add(1,"hi 3")
    d.add(2,"bye")

    for i in sorted(d.dict):
        print(i, d.dict[i])

