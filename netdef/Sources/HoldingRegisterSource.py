import logging

from ..Interfaces.IntegerInterface import IntegerInterface
from . import IntegerSource, Sources


@Sources.register("HoldingRegisterSource")
class HoldingRegisterSource(IntegerSource.IntegerSource):
    def unpack_unit_and_address(self):
        return map(int, self.key.split(":"))

    @staticmethod
    def pack_unit_and_address(unit, address):
        return "{}:{}".format(unit, address)
