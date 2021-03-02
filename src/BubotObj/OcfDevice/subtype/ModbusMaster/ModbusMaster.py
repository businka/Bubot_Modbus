from BubotObj.OcfDevice.subtype.Device.Device import Device
from BubotObj.OcfDevice.subtype.Device.QueueMixin import QueueMixin
from .__init__ import __version__ as device_version
from Bubot.Helpers.ExtException import ExtException, ExtTimeoutError, KeyNotFound
from aio_modbus_client.ModbusProtocolRtu import ModbusProtocolRtu as ModbusProtocol
from aio_modbus_client.TransportSocket import TransportSocket as ModbusSocket
from aio_modbus_client.TransportSerial import TransportSerial as ModbusSerial
from aio_modbus_client.ModbusProtocolOcf import OcfMessageRequest
import asyncio
import logging


# _logger = logging.getLogger(__name__)


class ModbusMaster(Device, QueueMixin):
    version = device_version
    file = __file__
    ModbusProtocol = ModbusProtocol
    template = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial_queue = asyncio.Queue()
        self.serial_queue_worker = None
        self.modbus = None

    async def on_pending(self):
        self.serial_queue_worker = asyncio.ensure_future(self.queue_worker(self.serial_queue, 'serial_queue'))
        self.init_modbus()
        await super().on_pending()

    def init_modbus(self):
        port = self.get_param('/oic/con', 'port')
        Modbus = ModbusSocket if port else ModbusSerial
        self.modbus = self.ModbusProtocol(
            Modbus(
                host=self.get_param('/oic/con', 'host'),
                port=port,
                logger=self.log
            ),
            timeout=self.get_param('/oic/con', 'timeout', 2),
            logger=self.log
        )

    async def execute(self, data):
        try:
            if self.need_change_serial(data):
                await self.set_serial_configuration(data)
            self.log.debug(data)
            message = OcfMessageRequest(**data)
            response = await self.modbus.execute(message, None)
            # self.log.debug('execute({0})={1}'.format(data, response))
            return response.b64decode()
        except KeyError as err:
            self.log.error(f'Не указан обязательный параметр {err}')
            raise KeyNotFound(detail=str(err), action='ModbusMaster.execute')
        except asyncio.TimeoutError as err:
            self.log.error('ExtTimeoutError')
            raise ExtTimeoutError(action='ModbusMaster.execute') from err
        except Exception as err:
            self.log.error(err)
            raise ExtException(parent=err, action='ModbusMaster.execute')

    async def set_serial_configuration(self, new_config):
        pass

    def need_change_serial(self, new):
        def check(name):
            return True if self.get_param('/oic/con', name) == new[name] else False

        if check("baudRate") and check("parity") and check("dataBits") and check("stopBits"):
            return False
        return True

    async def on_update_modbus_msg(self, message):
        result = await self.execute_in_queue(
            self.serial_queue,
            self.execute(
                message.cn,
            ), name='execute')
        return result

    def update_param(self, resource, name, new_value, **kwargs):
        if resource in ['/oic/con', 'oic/d']:
            kwargs['save_config'] = True
        changes = super().update_param(resource, name, new_value, **kwargs)
        if resource == '/oic/con' and ('host' in changes or 'post' in changes or 'timeout' in changes):
            self.init_modbus()
        return changes
