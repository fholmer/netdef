import os
import sys
import logging
import pathlib
from collections import OrderedDict
from configparser import ConfigParser, ExtendedInterpolation, InterpolationMissingOptionError

log = logging.getLogger(__name__)

class Config():
    def __init__(self, identifier, install_path, proj_path, default_config_string):

        self.IDENTIFIER = identifier

        if not install_path:
            install_path = os.path.dirname(__file__)
            #install_path = os.path.expanduser(install_path)

        if not proj_path:
            proj_path = os.getcwd()

        config_path = pathlib.Path(proj_path).joinpath("config")

        _config = ConfigParser(interpolation=ExtendedInterpolation())

        #Dette trikset gjør at option-nøkkel forblir case-sensitive
        _config.optionxform = str

        self._config = _config
        _config.add_section("install")
        _config.set("install", "path", install_path)
        _config.add_section("proj")
        _config.set("proj", "path", proj_path)

        _config.read_string(default_config_string)

        # dersom getfilesystemencoding returnerer ascii så vil vi ikke kunne lese konfigfiler med eksotiske tegn.
        # vi må derfor velge noe annet; getdefaultencoding() er et godt valg
        self.conf_encoding = sys.getfilesystemencoding()
        if self.conf_encoding == "ascii":
            self.conf_encoding = sys.getdefaultencoding()

        #self.read("{install_path}/data".format(install_path=install_path))
        self.read_default(config_path)

        self.verify(proj_path, config_path)

        if "config" in self._config:
            for ident, path in self.get_dict("config").items():
                self._config.read(path, encoding=self.conf_encoding)

        # denne filen skal ikke være redigerbare fra web eller filsystem
        # brukes til å låse bestemte konfiger. må derfor leses sist.
        self._config.read(
            "{config_path}/default.lock".format(
                config_path=config_path
                ),
                encoding=self.conf_encoding
            )

        # liste over konfiger som ikke skal være synlig i webadmin
        # settes med set_hidden_value-funksjonen
        self._hidden = {}

    def read_default(self, config_path):
        log.info("Read config from %s", config_path)

        self._config.read(
            "{config_path}/default.conf".format(
                config_path=config_path
                ),
                encoding=self.conf_encoding
            )
        self._config.read(
            "{config_path}/default.{os_name}.conf".format(
                config_path=config_path,
                os_name=os.name
                ),
                encoding=self.conf_encoding
            )

    def __call__(self, section, key, defaultvalue=None, add_if_not_exists=True):
        return self.config(section, key, defaultvalue)

    def config(self, section, key, defaultvalue=None, add_if_not_exists=True):
        try:
            if defaultvalue is None:
                return self._config[section][key]
            else:
                # typecast basert på defaultvalue
                return type(defaultvalue)(self._config[section][key])
        except (KeyError, InterpolationMissingOptionError):
            if add_if_not_exists:
                self.set_config(section, key, str(defaultvalue))
            return defaultvalue

    def set_config(self, section, key, value):
        self.add_section(section)
        self._config.set(section, key, value)

    def add_section(self, section):
        if not self._config.has_section(section):
            self._config.add_section(section)

    def set_hidden_value(self, section, key):
        if not section in self._hidden:
            self._hidden[section] = []
        if not key in self._hidden[section]:
            self._hidden[section].append(key)

    def is_hidden_value(self, section, key):
        if not section in self._hidden:
            return False
        return (key in self._hidden[section])
        
    def get_dict(self, section):
        return OrderedDict(self._config[section])

    def get_full_list(self):
        def walker():
            for section, keyval in self._config.items():
                try:
                    for key, val in keyval.items():
                        if self.is_hidden_value(section, key):
                            yield section, key, "****"
                        else:
                            yield section, key, val
                except InterpolationMissingOptionError as error:
                    yield section, "ERROR", repr(error)

        return walker()

    def verify(self, proj_path, config_path):
        proj_path = pathlib.Path(proj_path)
        if not proj_path.is_dir():
            raise ValueError("Error parsing config-files. proj-path {} not found".format(proj_path))

        config_path = pathlib.Path(config_path)
        if not config_path.is_dir():
            raise ValueError("Error parsing config-files. config-path {} not found".format(config_path))

        default_conf = config_path.joinpath("default.conf")
        if not default_conf.is_file():
            raise ValueError("Error parsing config-files. configfile {} not found".format(default_conf))

        if self.config("general", "identifier", "") != self.IDENTIFIER:
            raise ValueError("Error parsing config-files. [general]identifier {} not found".format(self.IDENTIFIER))

        if self.config("general", "version", 0.0) != 1:
            raise ValueError("Error parsing config-files. [general]version {} not found".format(1))
 
        return True

