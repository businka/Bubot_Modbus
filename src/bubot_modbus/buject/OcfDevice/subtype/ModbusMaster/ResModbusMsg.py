from bubot.OcfResource.OcfResource import OcfResource
from bubot_helpers.ExtException import ExtException

from Bubot_CoAP.defines import Codes


class ResModbusMsg(OcfResource):

    async def on_post(self, request, response):
        self.debug('post', request)
        try:
            result = await self.device.execute_in_queue(
                self.device.serial_queue,
                self.device.execute(
                    request.decode_payload(),
                ), name='execute')

            response.code = Codes.CHANGED.number
            response.content_type = self.actual_content_type
            response.encode_payload(result)
        except Exception as err:
            e = ExtException(parent=err)
            response.code = Codes.BAD_REQUEST.number
            response.content_type = self.actual_content_type
            response.encode_payload(e.to_dict())
        return self, response
