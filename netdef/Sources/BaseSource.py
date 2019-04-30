import enum
import copy
import datetime
from ..Interfaces.DefaultInterface import DefaultInterface

class StatusCode(enum.Enum):
    NONE = 0
    INITIAL = 1
    GOOD = 2
    INVALID = 3

class BaseSource():
    def __init__(self, key=None, value=None, controller=None, source=None, rule=None):
        #verdier
        self.get_value = None  # Ny verdi inn fra driver
        self.set_value = None  # Ny verdi ut fra uttrykk
        self.value = value  # cachet verdi fra get eller set når disse er behandlet
        self.set_callback = None # callback som skal kjøres når verdi settes fra utrykk

        # verdiens statuskode, ved oppstart er den NONE
        # første innhentede verdi fra controller er INITIAL
        # alle innhentede verdier etter dette vil ha GOOD eller INVALID
        self.status_code = StatusCode.NONE

        # når verdien ble oppdatert.
        # skal alltid være av typen datetime.datetime
        # dersom verdi ikke har medfølgende tidsstempel skal
        # controller selv sette denne med datetime.datetime.utcnow()
        self.source_time = None

        # kilder
        self.rule = rule # kontroller må benytte denne for å sende RUN_EXPRESSION til riktig kø
        self.controller = controller # regelmotor må benytte denne for å sende ADD_SOURCE til riktig kontroller
        self.source = source # kan brukes av kontroller eller uttrykk for å verifisere kilde-typen
        self.key = key # unik identifikasjon for kilden. kommer typisk fra en konfigfil som er parset av regelmotor

        # dette er en valgfri "wrapper" til verdien fra kontrolleren.
        # hensikten er å gjøre manipulering av verdi så enkel som mulig i uttrykk
        self.interface = DefaultInterface

    def __str__(self):
        "brukes til søk og print av kildedata"
        return self.get_reference() + " V:{}".format(self.value_as_string)

    def get_reference(self):
        """ Brukers av Rule.
            Benyttes til å identifisere like kilder. hvis to instanser returnerer samme referanse
            betyr dette at den ene instansen er overflødig og kan erstattes
        """
        return "C:{} S:{} R:{} K:{}".format(self.controller, self.source, self.rule, self.key)

    @property
    def value_as_string(self):
        """brukes primært av webgrensesnitt til å vise verdi i tabell.
        bør overstyres for å begrense visning av store data"""
        return str(self.value)

    @staticmethod
    def pack_subitems(value):
        """Benyttes av controller. Lager utdata som kan benyttes til å spørre
           etter etter en liste med inndata
        """
        return None

    @staticmethod
    def can_unpack_subitems(value):
        """ Benyttes av controller. Funksjon som bekrefter/avkrefter om inndata er
            en kjent liste av noe slag. hvis ja, så blir unpack_subitems brukt etterpå.
        """
        return False # kilder må overstyre denne. den er default av.

    @staticmethod
    def unpack_subitems(value):
        """ Benyttes av controller. Funksjon som parser svar fra kilde og
            yielder items funnet i verdi. Denne kan overstyres og
            tilpasses controller den skal brukes mot.
        """
        yield None

    @staticmethod
    def can_unpack_value(value):
        """ Benyttes av controller. Funksjon som bekrefter/avkrefter om inndata er
            kompatiblet med denne klassen. hvis ja, så blir unpack_value brukt etterpå.
        """
        return False # kilder må overstyre denne. den er default av.

    @staticmethod
    def unpack_value(key, source_time, value):
        """ Benyttes av controller. Funksjon som parser svar fra kilde og
            returnererfølgende tuple: (key, source_time, value)
            key kan så benyttes til å finne riktig instanse og oppdatere verdier
            denne kan overstyres og tilpasses controller den skal brukes mot.
        """
        return key, source_time, value

    def pack_value(self, value):
        """ Benyttes av controller. Funksjon som gjør om key og verdier til et format
            som kilden benytter. Denne kan overstyres og tilpasses controller den
            skal brukes mot.
        """
        return self.key, value
    
    def pack_add_source(self):
        """ Benyttes av controller. Dersom kilde må legges til i eksternt system
            for å endringer tilbake så kan denne funksjonen overstyres og tilpasses.
            Den er default av.
        """
        return False

    def copy_value(self):
        """ Lag en kopi av verdien slik at den er en ny instanse"""
        return copy.copy(self.value)

    def copy_get_value(self):
        """ Lag en kopi av verdien slik at den er en ny instanse"""
        return copy.copy(self.get_value)

    @property
    def get(self):
        """ Les verdi fra controller """
        return self.get_value

    @get.setter
    def get(self, val):
        """ controller skriver til get_value med denne funksjonen """
        self.get_value = val
        self.value = val

    @property
    def set(self):
        """ Les verdi fra uttrykk"""
        return self.set_value

    @set.setter
    def set(self, val):
        """ Utrykk skriver til set_value med denne funsjonen """
        if isinstance(val, DefaultInterface):
            val = val.value
        self.set_value = val
        self.value = val
        if self.set_callback:
            self.set_callback(self, val, datetime.datetime.utcnow())

    def register_set_callback(self, set_callback):
        """ Regelmotor kaller denne funksjonen.
            callback setter en WRITE_SOURCE melding til kontrollerens kø.
        """
        self.set_callback = set_callback
