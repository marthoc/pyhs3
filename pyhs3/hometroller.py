"""
Models a connection to a HomeSeer HomeTroller (or independent HomeSeer HS3 software installation).
Allows sending commands via JSON API and listening for device changes via ASCII interface.
"""

import logging
from asyncio import TimeoutError
from aiohttp import ContentTypeError

from .const import (DEFAULT_ASCII_PORT, DEFAULT_HTTP_PORT, DEFAULT_HTTP_TIMEOUT, DEFAULT_USERNAME, DEFAULT_PASSWORD,
                    REASON_DISCONNECTED, STATE_IDLE, STATE_STOPPED)
from .events import HomeSeerEvent
from .listener import ASCIIListener
from .zwave import get_zwave_device

_LOGGER = logging.getLogger(__name__)


class HomeTroller:

    def __init__(self, host, websession, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD,
                 http_port=DEFAULT_HTTP_PORT, ascii_port=DEFAULT_ASCII_PORT, http_timeout=DEFAULT_HTTP_TIMEOUT):
        self._host = host
        self._websession = websession
        self._username = username
        self._password = password
        self._http_port = http_port
        self._ascii_port = ascii_port
        self._http_timeout = http_timeout
        self._listener = ASCIIListener(self._host, ascii_port=self._ascii_port,
                                       async_message_callback=self._update_device_value,
                                       async_connection_callback=self.refresh_devices,
                                       async_disconnection_callback=self._disconnect_callback)
        self.devices = {}
        self.events = []

    @property
    def state(self):
        return self._listener.state

    async def initialize(self):
        await self._get_devices()
        await self._get_events()

    async def start_listener(self):
        self._listener.state = STATE_IDLE
        await self._listener.connection_handler()

    async def stop_listener(self):
        self._listener.state = STATE_STOPPED
        await self._listener.connection_handler()

    async def _request(self, method, params=None, json=None):
        """Make an API request"""
        url = 'http://{}:{}@{}:{}/JSON'.format(self._username, self._password, self._host, self._http_port)

        try:
            async with self._websession.request(method, url, params=params, json=json,
                                                timeout=self._http_timeout) as result:
                result.raise_for_status()
                _LOGGER.debug('HomeSeer request response: {}'.format(await result.text()))
                return await result.json()

        except ContentTypeError:
            _LOGGER.debug('HomeSeer returned non-JSON response: {}'.format(await result.text()))

        except TimeoutError:
            _LOGGER.error('Timeout while requesting HomeSeer data from {}:{}'.format(self._host, self._http_port))

        except Exception as err:
            _LOGGER.error('HomeSeer HTTP Request error: {}'.format(err))

    async def _get_devices(self):
        try:
            params = {
                'request': 'getstatus'
            }
            result = await self._request('get', params=params)

            all_devices = result['Devices']

            params = {
                'request': 'getcontrol'
            }
            result = await self._request('get', params=params)

            control_data = result['Devices']

            for device in all_devices:
                dev = get_zwave_device(device, control_data, self._request)
                if dev is not None:
                    self.devices[dev.ref] = dev

        except TypeError:
            _LOGGER.error('Error retrieving HomeSeer devices!')

    async def _get_events(self):
        try:
            params = {
                'request': 'getevents'
            }
            result = await self._request('get', params=params)

            all_events = result['Events']

            for event in all_events:
                ev = HomeSeerEvent(event, self._request)
                self.events.append(ev)

        except TypeError:
            _LOGGER.error('Error retrieving HomeSeer events!')

    async def _update_device_value(self, device_ref, value):
        try:
            device = self.devices[int(device_ref)]
            device.update_value(value)
            _LOGGER.debug('HomeSeer device \'{}\' ({}) updated to: {}'.format(
                device.name, device.ref, device.value))
        except KeyError:
            _LOGGER.debug('HomeSeer update received for unsupported device: {}'.format(
                device_ref))

    async def _disconnect_callback(self):
        for device in self.devices.values():
            device.update_value(None, REASON_DISCONNECTED)

    async def refresh_devices(self, reason=None):
        try:
            params = {
                'request': 'getstatus'
            }
            result = await self._request('get', params=params)

            all_devices = result['Devices']

        except TypeError:
            _LOGGER.error('Error retrieving HomeSeer data for refresh!')
            return

        for device in all_devices:
            try:
                dev = self.devices[device['ref']]
                dev.update_value(device['value'], reason)
                _LOGGER.debug('HomeSeer device \'{}\' ({}) refreshed to: {}'.format(
                    dev.name, dev.ref, dev.value))
            except KeyError:
                _LOGGER.debug('HomeSeer refresh data retrieved for unsupported device type: {} ({})'.format(
                    device['device_type_string'], device['ref']))
