import logging
from opcua.ua import NodeId, VariantType
from . import BaseSource, Sources
from ..Interfaces import DefaultInterface, IntegerInterface, FloatInterface, BytestringInterface
from ..Interfaces.datamessage import DataDefinition

supported_types = {vt.name.lower(): vt.name for vt in VariantType}

@Sources.register("OpcUaVariantSource")
class OpcUaVariantSource(BaseSource.BaseSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interface = DefaultInterface.DefaultInterface

        self._nodeid = self.key
        self._varianttype = None
        self._is_writable = True

        if DataDefinition.is_uri(self.key):

            #test if nodeid is valid. raises error if not
            datadef = DataDefinition.from_uri(self.key)
            self._nodeid = NodeId.from_string(datadef.key).to_string()

            #test if varianttype is supported
            _varianttype_name = datadef.datatype.lower().strip()
            if not _varianttype_name in supported_types.keys():
                raise KeyError("{} not supported", datadef.datatype.varianttype)

            #test if varianttype is valid. raises error if not
            self._varianttype = getattr(VariantType, supported_types[_varianttype_name])

            # select interface
            if self._varianttype == VariantType.ByteString:
                self.interface = BytestringInterface.ByteStringInterface
            elif self._varianttype in (VariantType.Float, VariantType.Double):
                self.interface = FloatInterface.FloatInterface
            elif self._varianttype in (
                    VariantType.Int16,
                    VariantType.UInt16,
                    VariantType.Int32,
                    VariantType.UInt32,
                    VariantType.Int64,
                    VariantType.UInt64
                ):
                self.interface = IntegerInterface.IntegerInterface
            else:
                self.interface = DefaultInterface.DefaultInterface

            # True if value is truthfull.
            self._is_writable = True if datadef.access != 'ro' else False

    def get_varianttype(self):
        "Returns the varianttype from the source"
        return self._varianttype

    def get_nodeid(self):
        "Returns the nodeid from the source"
        return self._nodeid

    def is_writable(self):
        "Returns True if source is writable for the opcua client"
        return self._is_writable

    @property
    def value_as_string(self):
        """
        This function is used by webadmin to visualize the value as string
        Bytedata is truncated to limit the size of the string
        """
        if self.value and isinstance(self.value, bytes):
            n = len(self.value)
            return "<{}...><data len:{}>".format(self.value[:10], n)
        else:
            return super().value_as_string
