
class FakeLogger(object):
    def __init__(self):
        self._info =""
        self._debug =""
    def info(self,message):
        self._info +="\nINFO "+message

    def debug(self,message):
        self._debug +="\nDEBUG "+message
    @property
    def lines(self):
        return self._info.split("\n")
    @property
    def debug_lines(self):
        return self._debug.split("\n")

