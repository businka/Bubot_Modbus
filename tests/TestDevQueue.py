import unittest
from .async_test import async_test
from BubotObj.OcfDevice.subtype.Device.QueueMixin import QueueMixin
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s',
                    )

class TestDevQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    async def waiting(self, second):
        print(second)
        await asyncio.sleep(second)
        return second

    @async_test
    async def test_queue(self):
        dev = QueueMixin()
        dev.queue = asyncio.PriorityQueue()
        tasks = []
        worker = asyncio.create_task(dev.queue_worker(dev.queue))
        await asyncio.sleep(0.001)
        tasks.append(dev.execute_in_queue(dev.queue, self.waiting(2), 10))
        tasks.append(dev.execute_in_queue(dev.queue, self.waiting(1), 5))
        tasks.append(dev.execute_in_queue(dev.queue, self.waiting(6), 1))

        res = await asyncio.gather(*tasks, return_exceptions=True)

        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass
        pass

