from ...Sources.BaseSource import StatusCode

class Expression():
    def __init__(self, expression, filename):
        self.expression = expression
        self.filename = filename
        self.args = []
        self.kwargs = {}
        self.result = None
        self._enabled = True

    def __str__(self):
        args = ",".join(str(arg) for arg in self.args)
        return "F:{} E:{} A:{} K:{} R:{}".format(self.filename, self.expression, args, self.kwargs, self.result)

    def add_arg(self, arg):
        self.args.append(arg)

    def add_kwarg(self, keyword, arg):
        self.kwargs[keyword] = arg

    def get_args(self, source_instance=None):
        return tuple(Argument(arg, arg is source_instance) for arg in self.args)

    def get_kwargs(self):
        return self.kwargs

    def execute(self, args, kwargs):
        if self._enabled:
            self.result = self.expression(*args, **kwargs)
            return self.result
        else:
            return None
    
    def disable(self):
        # if there is problems with the expression it can
        # be automaticly disabled by calling this function
        self._enabled = False

class Argument():
    def __init__(self, source_instance, instigator):

        # referanse til source instansen
        # husk denne er levende. altså verdien kan plutselig endres av en annen
        # tråd eller prosess. typisk controlleren.
        self.instance = source_instance

        # følgende verdiene er ikke levende:

        # value er en lokal kopi av verdien. denne vil ikke endre seg
        self.value = self.instance.copy_get_value()

        # en klasse med hjelpefunksjoner for verdien.
        self.interface = source_instance.interface(self.value)

        # instigator er True hvis verdien er grunnen til at uttrykket blir kjørt
        if instigator:
            self.new = self.instance.status_code == StatusCode.INITIAL
            self.update = not (self.new or self.instance.status_code == StatusCode.NONE)
        else:
            self.new = False
            self.update = False

    @property
    def get(self):
        return self.instance.get

    @property
    def set(self):
        return self.instance.set

    @set.setter
    def set(self, value):
        self.instance.set = value

    @property
    def key(self):
        return self.instance.key
