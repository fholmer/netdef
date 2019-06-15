from ...Sources.BaseSource import StatusCode

class Expression():
    """
    A class containing a reference to the expression-function and references
    to the source-instances that will become arguments to the expression
    function

    - expression -- a reference to the actual function
    - filename (string) -- filename of the module where the function is found

    """
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
        "arg: this should be a source instance"
        self.args.append(arg)

    def add_kwarg(self, keyword, arg):
        """
        This could be anything. This function exist for
        you to extend arguments for the expressions. netdef itself do not use this
        """
        self.kwargs[keyword] = arg

    def get_args(self, source_instance=None):
        """Wrap each source-instance into its own Argument instance
        Return a tuple of Arguments
        """
        return tuple(Argument(arg, arg is source_instance) for arg in self.args)

    def get_kwargs(self):
        return self.kwargs

    def execute(self, args, kwargs):
        "Execute the expression-function with given arguments"
        if self._enabled:
            self.result = self.expression(*args, **kwargs)
            return self.result
        else:
            return None
    
    def disable(self):
        """
        If there is problems with the expression it can
        be automaticly disabled by calling this function
        """
        self._enabled = False

class Argument():
    """
    A wrapper for source instances.

    - source_instance -- An source instance
    - instigator: (boolean) -- True if given source instance triggered the execution

    """

    def __init__(self, source_instance, instigator):

        # referanse til source instansen
        # husk denne er levende. altså verdien kan plutselig endres av en annen
        # tråd eller prosess. typisk controlleren.
        self._instance = source_instance

        # følgende verdiene er ikke levende:

        # value er en lokal kopi av verdien. denne vil ikke endre seg
        self._value = self._instance.copy_get_value()

        # instigator er True hvis verdien er grunnen til at uttrykket blir kjørt
        if instigator:
            self._new = self._instance.status_code == StatusCode.INITIAL
            self._update = not (self._new or self._instance.status_code == StatusCode.NONE)
        else:
            self._new = False
            self._update = False


    @property
    def instance(self):
        "reference to the source instance"
        return self._instance

    @property
    def value(self):
        "a frozen copy of the value in self.instance.get"
        return self._value

    @property
    def new(self):
        "Returns True if source triggered the expression and this is the first value. (StatusCode.INITIAL)"
        return self._new

    @property
    def update(self):
        "Returns True if source triggered the expression. (StatusCode.GOOD or INVALID)"
        return self._update

    @property
    def get(self):
        """
        Returns the value from source instance. NB! this is not a *frozen* copy
        of the value. It may change if the controller updates the value.
        """
        return self._instance.get

    @property
    def set(self):
        """
        Write a new value to the source. This will trigger a WRITE_SOURCE message to the controller.
        """
        return self._instance.set

    @set.setter
    def set(self, value):
        self._instance.set = value

    @property
    def key(self):
        "Returns the key attribute from source instance"
        return self._instance.key
