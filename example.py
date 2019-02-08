import asyncio
import logging
import sys

from aiohttp import ClientSession


async def main():

    if len(sys.argv) < 2:
        print('Usage: python example.py ipaddress')
        exit(1)

    host = sys.argv[1]
    websession = ClientSession()

    from pyhs3 import HomeTroller
    homeseer = HomeTroller(host, websession)

    await homeseer.initialize()

    print('-----------------')
    print('HomeSeer Devices:')
    print('-----------------')
    for device in homeseer.devices.values():
        print('Name: {} (Type: {})'.format(device.name, device.device_type_string))

    print('----------------')
    print('HomeSeer Events:')
    print('----------------')
    for event in homeseer.events:
        print('Group: {}, Name: {}'.format(event.group, event.name))

    print()
    print('Starting listener on the event loop!')
    await homeseer.start_listener()

logging.basicConfig(level=logging.DEBUG)
loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
