import asyncio

from aio_modbus_client.ModbusDevice import ModbusDevice as ModbusDevice
from aio_modbus_client.ModbusProtocolOcf import ModbusProtocolOcf
from bubot.buject.OcfDevice.subtype.Device.Device import Device
from bubot.core.ResourceLink import ResourceLink
from bubot_helpers.ActionDecorator import async_action
from bubot_helpers.ExtException import ExtException, ExtTimeoutError


# _logger = logging.getLogger(__name__)


class ModbusSlave(Device):
    file = __file__

    ModbusDevice = ModbusDevice

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial_queue = asyncio.Queue()
        self.serial_queue_worker = None
        self.modbus = None
        self.link_master = None

    async def on_pending(self):
        try:
            if not self.modbus:
                self.set_modbus()
            master_link, master_response = await self.check_link('/oic/con', 'master')

            if master_response:
                await super().on_pending()
        except Exception as err:
            raise ExtException(parent=err, action='ModbusSlave.on_pending')

    def set_modbus(self):
        self.link_master = ResourceLink.init(self.get_param('/oic/con', 'master'))
        self.modbus = self.ModbusDevice(self.get_param('/oic/con', 'slave'), ModbusProtocolOcf(self))

    @async_action
    async def find_devices(self, **kwargs):
        notify = kwargs.get('notify')

        self.link_master = ResourceLink.init(self.get_param('/oic/con', 'master'))
        modbus = self.ModbusDevice(self.get_param('/oic/con', 'slave'), ModbusProtocolOcf(self))
        founded_devices = await modbus.find_devices(notify=notify, timeout_exception=ExtTimeoutError)
        result = []

        for slave_id in founded_devices:
            device = self.init_from_config(self.data)
            name = f'{device.get_device_name()} (slave: 0x{slave_id:x})'
            device.set_param('/oic/con', 'slave', slave_id)
            device.set_param('/oic/d', 'n', name)
            result.append(dict(
                _id=device.get_device_id(),
                name=name,
                links=device.get_discover_res(),
                # _actions=driver.get_install_actions()
            ))
        return result
