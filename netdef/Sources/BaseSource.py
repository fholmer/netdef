import enum
import copy
import datetime
from ..Interfaces.DefaultInterface import DefaultInterface

class StatusCode(enum.Enum):
    """
    Used to indicate the quality of a value in BaseSource.status_code
    
    NONE: Value is not set yet.
    INITIAL: First value. you might have to update cashes with this value at application startup.
    GOOD: A normal value update.
    INVALID: A value update where the value is not to be trusted.
    """
    NONE = 0
    INITIAL = 1
    GOOD = 2
    INVALID = 3

class BaseSource():
    def __init__(self, key=None, value=None, controller=None, source=None, rule=None):
        #verdier

        # cache
        self.value = value  # cachet verdi fra get_value eller set_value når disse er behandlet

        # verdiens statuskode, ved oppstart er den NONE
        # første innhentede verdi fra controller er INITIAL
        # alle innhentede verdier etter dette vil ha GOOD eller INVALID
        self.status_code = StatusCode.NONE

        # når verdien ble oppdatert.
        # skal alltid være av typen datetime.datetime
        # dersom verdi ikke har medfølgende tidsstempel skal
        # controller selv sette denne med datetime.datetime.utcnow()
        self.source_time = None
        self.source_datatype = None

        # Ny verdi inn fra driver
        self.get_value = None
        self.get_source_time = None
        self.get_status_code = None
        self.get_origin = None

        # Ny verdi ut fra uttrykk
        self.set_value = None
        self.set_source_time = None
        self.set_status_code = None
        self.set_origin = None
        self.set_callback = None # callback som skal kjøres når verdi settes fra utrykk

        # kilder
        self.rule = rule # kontroller må benytte denne for å sende RUN_EXPRESSION til riktig kø
        self.controller = controller # regelmotor må benytte denne for å sende ADD_SOURCE til riktig kontroller
        self.source = source # kan brukes av kontroller eller uttrykk for å verifisere kilde-typen
        self.key = key # unik identifikasjon for kilden. kommer typisk fra en konfigfil som er parset av regelmotor

        # dette er en valgfri "wrapper" til verdien fra kontrolleren.
        # hensikten er å gjøre manipulering av verdi så enkel som mulig i uttrykk
        self.interface = DefaultInterface

    def __str__(self):
        # brukes til søk og print av kildedata
        return self.get_reference() + " R: {} V:{}".format(self.rule, self.value_as_string)

    def get_reference(self):
        """
        Used to identify similar sources. if two instances return the same reference
        this means that one instance is redundant and can be replaced
        """
        # Brukers av Rule.
        # Benyttes til å identifisere like kilder. hvis to instanser returnerer samme referanse
        # betyr dette at den ene instansen er overflødig og kan erstattes
        return "C:{} S:{} K:{}".format(self.controller, self.source, self.key)

    @property
    def value_as_string(self):
        """
        Is primarily used by web interfaces to display value in table.
        Can be overridden to limit the display of large data.
        Example::

            @property
            def value_as_string(self):
                if self.value and isinstance(self.value, bytes):
                    n = len(self.value)
                    return "<{}...><data len:{}>".format(self.value[:10], n)
                else:
                    return super().value_as_string
        """
        # brukes primært av webgrensesnitt til å vise verdi i tabell.
        # bør overstyres for å begrense visning av store data
        return str(self.value)

    @staticmethod
    def pack_subitems(value):
        """
        Creates output that can be used to query for a list of inputs
        """
        # Benyttes av controller. Lager utdata som kan benyttes til å spørre
        # etter etter en liste med inndata
        return None

    @staticmethod
    def can_unpack_subitems(value):
        """
        Function that confirms / decides on input data a known list.
        If so, then unpack_subitems can be used afterwards.

        Example::

            def parse_response(self, response):
                for parser in self.get_parsers():
                    if parser.can_unpack_subitems(response):
                        yield from parser.unpack_subitems(response)

        """
        # """ Benyttes av controller. Funksjon som bekrefter/avkrefter om inndata er
        #     en kjent liste av noe slag. hvis ja, så blir unpack_subitems brukt etterpå.
        # """
        return False # kilder må overstyre denne. den er default av.

    @staticmethod
    def unpack_subitems(value):
        """
        Function that parses response from source and yield items found in value.
        This can be overridden and adapted to the controller it is to be used in.

        Example::

            def parse_response(self, response):
                for parser in self.get_parsers():
                    if parser.can_unpack_subitems(response):
                        yield from parser.unpack_subitems(response)

        """
        # """ Benyttes av controller. Funksjon som parser svar fra kilde og
        #     yielder items funnet i verdi. Denne kan overstyres og
        #     tilpasses controller den skal brukes mot.
        # """
        yield None

    @staticmethod
    def can_unpack_value(value):
        """
        Function that confirms / determines if the input data is compatible with this class.
        If so, unpack_value should be used afterwards.

        Example::

            def parse_item(self, item):
                for parser in self.get_parsers():
                    if parser.can_unpack_value(item):
                        key, source_time, value = parser.unpack_value(item)
                        self.send_datachange(key, source_time, value)

        """
        # """ Benyttes av controller. Funksjon som bekrefter/avkrefter om inndata er
        #     kompatiblet med denne klassen. hvis ja, så blir unpack_value brukt etterpå.
        # """
        return False # kilder må overstyre denne. den er default av.

    @staticmethod
    def unpack_value(key, source_time, value):
        """
        Function that parses response from source and returns following tuple: (key, source_time, value)
        Key can then be used to find the right instance and update values.

        Can be overridden and adapted to the controller it is to be used in.

        :returns: tuple(key, source_time, value)
        :rtype: tuple

        Example::

            def parse_item(self, item):
                for parser in self.get_parsers():
                    if parser.can_unpack_value(item):
                        key, source_time, value = parser.unpack_value(item)
                        self.send_datachange(key, source_time, value)

        """
        # """ Benyttes av controller. Funksjon som parser svar fra kilde og
        #     returnererfølgende tuple: (key, source_time, value)
        #     key kan så benyttes til å finne riktig instanse og oppdatere verdier
        #     denne kan overstyres og tilpasses controller den skal brukes mot.
        # """
        return key, source_time, value

    def pack_value(self, value):
        """ 
        Function that converts key and values into a format that the source uses.
        Can be overridden and adapted to the controller it is to be used in.

        Example::

            def handle_write_source(self, incoming, value, source_time):
                data = incoming.pack_value(value, source_time)
                topic, payload = incoming.make_message(incoming.key, data)
                self.publish_data_item(topic, payload)
                
        """
        # """ Benyttes av controller. Funksjon som gjør om key og verdier til et format
        #     som kilden benytter. Denne kan overstyres og tilpasses controller den
        #     skal brukes mot.
        # """
        return self.key, value
    
    def pack_add_source(self):
        """
        Used if source must be added to external system. I.e. a subscription.
        Can be overridden and customized.
        """
        # """ Benyttes av controller. Dersom kilde må legges til i eksternt system
        #     for å endringer tilbake så kan denne funksjonen overstyres og tilpasses.
        #     Den er default av.
        # """
        return False

    def copy_value(self):
        """ Shallow copy of the value """
        return copy.copy(self.value)

    def copy_get_value(self):
        """ Shallow copy of the value """
        return copy.copy(self.get_value)

    @property
    def get(self):
        """ Get the value that is updated by the controller """
        return self.get_value

    @get.setter
    def get(self, val):
        """ Set the value """
        # controller skriver til get_value med denne funksjonen
        self.get_value = val
        self.value = val

    @property
    def set(self):
        """ Get the value that is updated by expressions """
        return self.set_value

    @set.setter
    def set(self, val):
        """ Set the value """
        # Utrykk skriver til set_value med denne funsjonen
        if isinstance(val, DefaultInterface):
            val = val.value
        self._set_set_value(val, None, True, "expression")

    def _set_set_value(self, value, stime, status_ok, origin):
        """
        Backend for `set` and `set_value_from_string`

        :param value: value to be set
        :param (None or datetime.datetime) stime: timestamp when the value was changed
        :param bool status_ok: True if value is good
        :param str origin: who set the value

        """
        self.set_value = value
        self.set_status_code = StatusCode.GOOD if status_ok else StatusCode.INVALID
        self.set_source_time = datetime.datetime.utcnow() if stime is None else stime
        self.set_origin = origin
        self.value = value
        if self.set_callback:
            self.set_callback(self, value, self.set_source_time)

    def register_set_callback(self, set_callback):
        """
        Register the callback that sends WRITE_SOURCE message to the controller queue.
        """
        # Regelmotor kaller denne funksjonen.
        # callback setter en WRITE_SOURCE melding til kontrollerens kø.
        self.set_callback = set_callback

    def can_set_value_from_string(self):
        """
        Returns True if the value can be converted from string to its given
        datatype. Only `builtins.int`, `str` and `float` have built-in support, but aditional
        types can be implemented by this function and `set_value_from_string`

        """
        if isinstance(self.set_value, (int, str, float)):
            return True
        elif isinstance(self.get_value, (int, str, float)):
            return True
        else:
            return False
    
    def set_value_from_string(self, value, stime=None, status_ok=True, origin=""):
        """
        Converts given value to correct datatype and sends a WRITE_SOURCE message
        to controller.

        This function is called when a value change is triggered from
        :menuselection:`Webadmin --> Sources --> Edit`

        :param value: value to be set
        :param (None or datetime.datetime) stime: timestamp when the value was changed
        :param bool status_ok: True if value is good
        :param str origin: who set the value

        """
        if isinstance(self.set_value, (int, str, float)):
            val = type(self.set_value)(value)
        elif isinstance(self.get_value, (int, str, float)):
            val = type(self.get_value)(value)
        else:
            val = str(val)
        self._set_set_value(val, stime, status_ok, origin)
