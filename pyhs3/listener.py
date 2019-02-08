"""ASCII/Telnet listener for HomeSeer."""

import asyncio
import logging
from .const import (REASON_RECONNECTED, STATE_IDLE, STATE_LISTENING, STATE_STOPPED)
from .errors import HomeSeerASCIIConnectionError

_LOGGER = logging.getLogger(__name__)


class ASCIIListener:

    def __init__(self, host, **kwargs):
        self._host = host
        self._port = kwargs.get('ascii_port', 11000)
        self._async_message_callback = kwargs.get('async_message_callback')
        self._async_disconnection_callback = kwargs.get('async_disconnection_callback')
        self._async_reconnection_callback = kwargs.get('async_connection_callback')
        self._reader = None
        self._writer = None
        self._reconnect_flag = False
        self._state = STATE_IDLE
        self._flag = True

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    async def _start_listener(self):
        connection = asyncio.open_connection(self._host, self._port)
        try:
            self._reader, self._writer = await asyncio.wait_for(connection, timeout=3)
            _LOGGER.info('HomeSeer ASCII Listener connected to {}:{}'.format(self._host, self._port))
            self._state = STATE_LISTENING

            self._flag = True
            asyncio.get_event_loop().create_task(self._pinger())

            if self._reconnect_flag and self._async_reconnection_callback is not None:
                await self._async_reconnection_callback(reason=REASON_RECONNECTED)
            self._reconnect_flag = False

            while True:
                msg = await self._reader.readline()
                _LOGGER.debug('HomeSeer raw ASCII message received: {}'.format(msg))
                if msg == b'':
                    raise HomeSeerASCIIConnectionError
                else:
                    await self._handle_message(msg.decode())

        except HomeSeerASCIIConnectionError:
            _LOGGER.error('Empty ASCII message received, connection error')
            await self._handle_disconnect()

        except asyncio.TimeoutError:
            _LOGGER.error('HomeSeer ASCII listener connect timed out')
            await self._handle_disconnect()

        except Exception as err:
            _LOGGER.error('HomeSeer ASCII listener error: {}'.format(err))
            await self._handle_disconnect()

    async def _handle_message(self, raw):
        msg = raw.split(',')
        self._flag = True
        if msg[0] == 'DC' and self._async_message_callback is not None:
            await self._async_message_callback(msg[1], msg[2])
        else:
            _LOGGER.debug('HomeSeer unhandled ASCII message type received: {}'.format(msg[0]))

    async def _handle_disconnect(self):
        self._reconnect_flag = True
        if self._writer is not None:
            self._writer.close()

        if self._async_disconnection_callback is not None:
            await self._async_disconnection_callback()

        await self.connection_handler()

    async def _pinger(self):
        while True:
            if self.state == STATE_LISTENING:
                if self._flag:
                    self._flag = False
                    _LOGGER.debug('Sending ping...')
                    self._writer.write('vr\r\n'.encode())
                    await self._writer.drain()
                    await asyncio.sleep(120)
                else:
                    _LOGGER.debug('Ping timeout, closing ASCII connection')
                    self._writer.close()
                    break
            else:
                break

    async def connection_handler(self):
        if self.state == STATE_STOPPED:
            _LOGGER.debug('Stopping and closing ASCII listener')
            self._reconnect_flag = True
            if self._writer is not None:
                self._writer.close()
        else:
            if self._reconnect_flag:
                time = 10
                _LOGGER.info('Reconnecting ASCII Listener in {} seconds...'.format(time))
                await asyncio.sleep(time)
            _LOGGER.debug('Connecting ASCII listener to {}:{}'.format(self._host, self._port))
            self._state = STATE_IDLE
            asyncio.get_event_loop().create_task(self._start_listener())
