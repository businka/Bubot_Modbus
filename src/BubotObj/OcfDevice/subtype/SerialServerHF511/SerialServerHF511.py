from .__init__ import __version__ as device_version
from BubotObj.OcfDevice.subtype.ModbusMaster.ModbusMaster import ModbusMaster
from aio_modbus_client.ModbusProtocolRtuHF5111 import ModbusProtocolRtuHF5111 as ModbusProtocol


class SerialServerHF511(ModbusMaster):
    version = device_version
    file = __file__
    ModbusProtocol = ModbusProtocol
