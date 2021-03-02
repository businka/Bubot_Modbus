import unittest
import asyncio
from BubotObj.OcfDevice.subtype.SerialServerHF511.SerialServerHF511 import SerialServerHF511 as Device
from Bubot.Core.OcfMessage import OcfRequest
from aio_modbus_client.ModbusProtocolOcf import OcfMessageRequest
from Bubot.Core.TestHelper import async_test, wait_run_device, get_config_path
from Bubot.Helpers.ExtException import KeyNotFound, ExtTimeoutError
import logging


class TestSerialServerHF511(unittest.TestCase):
    pass
    config = {
        '/oic/con': {
            'host': '192.168.1.25',
            'port': 502,
            'serial': {
                'baudRate': 9600,
                'parity': 0,
                'dataBits': 8,
                'stopBits': 2,
            },
            'udpCoapUnicastPort': 17772,
            'udpCoapIPv4': False,
            'udpCoapIPv6': True
        }
    }


    @async_test
    async def setUp(self, **kwargs):
        logging.basicConfig(level=logging.DEBUG)
        self.config_path = get_config_path(__file__)
        self.device = Device.init_from_config(self.config, path=self.config_path)
        pass

    @async_test
    async def test_init(self, **kwargs):
        # self.assertIn('/light', self.device.data)
        # self.assertListEqual(self.device.data['/light']['rt'], ['oic.r.switch.binary', 'oic.r.light.brightness'])
        pass

    @async_test
    async def test_on_init(self, **kwargs):
        await self.device.on_init()
        pass

    @async_test
    async def test_echo_post_message(self, **kwargs):
        device_task = await wait_run_device(self.device)
        # from aio_modbus_client.ModbusProtocolEcho import ModbusProtocolEcho
        pdu = '\x00\x02\x00\x01'
        # self.device.modbus = ModbusProtocolEcho({
        #     pdu: '\x01\x00\x01'
        # })

        data = dict(
            slave=0x78,
            function=16,
            pdu=OcfMessageRequest.b64decode(pdu.encode()),
            answerSize=10,
            baudRate=9600,
            parity=0,
            stopBits=2,
            dataBits=8
        )
        message = OcfRequest(**dict(op='update', to=dict(href='/modbus_msg'), cn=data))
        result = await self.device.on_post_request(message)
        self.assertEqual(result, '\x01\x00\x01')
        pass

    @async_test
    async def test_discovery(self):
        device_task = await wait_run_device(self.device)
        resource = await self.device.coap.discovery_resource()
        self.assertIn(self.device.get_param('/oic/d', 'di'), resource)

    @async_test
    async def test_run(self, **kwargs):
        self.device.run()
        # result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_local_discovery(self, **kwargs):
        msg = OcfRequest(**dict(
            uri_path=['oic', 'res'],
            operation='get'
        ))
        res = self.device.on_get_request(msg)
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_echo_post_message_without_host(self, **kwargs):
        self.device.set_param('/oic/con', 'host', '')
        device_task = await wait_run_device(self.device)
        # from aio_modbus_client.ModbusProtocolEcho import ModbusProtocolEcho
        pdu = '\x00\x02\x00\x01'
        # self.device.modbus = ModbusProtocolEcho({
        #     pdu: '\x01\x00\x01'
        # })

        data = dict(
            slave=0x78,
            function=16,
            pdu=OcfMessageRequest.b64decode(pdu.encode()),
            answerSize=10,
            baudRate=9600,
            parity=0,
            stopBits=2,
            dataBits=8
        )
        message = OcfRequest(**dict(op='update', to=dict(href='/modbus_msg'), cn=data))
        with self.assertRaises(KeyNotFound):
            await self.device.on_post_request(message)
        pass

    @async_test
    async def test_echo_post_message_timeout_host(self, **kwargs):
        self.device.set_param('/oic/con', 'host', '192.168.168.168')
        device_task = await wait_run_device(self.device)
        # from aio_modbus_client.ModbusProtocolEcho import ModbusProtocolEcho
        pdu = '\x00\x02\x00\x01'
        # self.device.modbus = ModbusProtocolEcho({
        #     pdu: '\x01\x00\x01'
        # })

        data = dict(
            slave=0x78,
            function=16,
            pdu=OcfMessageRequest.b64decode(pdu.encode()),
            answerSize=10,
            baudRate=9600,
            parity=0,
            stopBits=2,
            dataBits=8
        )
        message = OcfRequest(**dict(op='update', to=dict(href='/modbus_msg'), cn=data))
        with self.assertRaises(ExtTimeoutError):
            await self.device.on_post_request(message)
