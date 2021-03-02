import asyncio
from BubotObj.OcfDevice.subtype.Device.Device import Device
from Bubot.Core.DeviceLink import ResourceLink
from aio_modbus_client.ModbusProtocolOcf import ModbusProtocolOcf
from aio_modbus_client.ModbusDevice import ModbusDevice as ModbusDevice
from Bubot.Helpers.ExtException import ExtException, ExtTimeoutError
from Bubot.Helpers.Helper import Helper
from Bubot.Helpers.Action import async_action


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

    async def check_connection_to_master(self):
        try:
            if await self.request('retrieve', self.link_master):
                return True
            return False
        except Exception:
            return False

    async def on_pending(self):
        if not self.modbus:
            self.set_modbus()

        master = await self.check_connection_to_master()
        for i in range(1):  # пытаемся достучаться
            if not master:
                self.log.debug('waiting modbus')
                await asyncio.sleep(i + 1)
                master = await self.check_connection_to_master()

        if not master:
            link = ResourceLink.init_from_link(self.get_param('/oic/con', 'master'))
            link = await self.find_resource_by_link(link)
            if link:
                self.log.debug('master found')
                self.set_param('/oic/con', 'master', link.data)
                self.save_config()
                self.set_modbus()
            pass
        if master:
            await super().on_pending()

    def set_modbus(self):
        self.link_master = self.get_param('/oic/con', 'master')
        self.modbus = self.ModbusDevice(self.get_param('/oic/con', 'slave'), ModbusProtocolOcf(self))

    @async_action
    async def find_devices(self, **kwargs):
        notify = kwargs.get('notify')

        self.link_master = self.get_param('/oic/con', 'master')
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
