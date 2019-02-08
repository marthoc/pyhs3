"""Models Z-Wave devices."""

from .const import (DEVICE_ZWAVE_BATTERY, DEVICE_ZWAVE_CENTRAL_SCENE,
                    DEVICE_ZWAVE_DOOR_LOCK, DEVICE_ZWAVE_SENSOR_BINARY, DEVICE_ZWAVE_SWITCH_MULTILEVEL,
                    DEVICE_ZWAVE_SWITCH, DEVICE_ZWAVE_SWITCH_BINARY)
from .device import HomeSeerDevice


class ZWaveBattery(HomeSeerDevice):

    pass


class ZWaveCentralScene(HomeSeerDevice):

    pass


class ZwaveDoorLock(HomeSeerDevice):

    async def lock(self):
        json = {
            'action': 'controlbyvalue',
            'deviceref': self.ref,
            'value': self.on_value
        }

        await self._request('post', json=json)

    async def unlock(self):
        json = {
            'action': 'controlbyvalue',
            'deviceref': self.ref,
            'value': self._off_value
        }

        await self._request('post', json=json)


class ZWaveSensorBinary(HomeSeerDevice):

    pass


class ZWaveSwitch(HomeSeerDevice):

    async def on(self):
        json = {
            'action': 'controlbyvalue',
            'deviceref': self.ref,
            'value': self.on_value
        }

        await self._request('post', json=json)

    async def off(self):
        json = {
            'action': 'controlbyvalue',
            'deviceref': self.ref,
            'value': self._off_value
        }

        await self._request('post', json=json)


class ZWaveSwitchMultilevel(ZWaveSwitch):

    async def dim(self, percent: int):
        value = int(self.on_value * (percent/100))

        json = {
            'action': 'controlbyvalue',
            'deviceref': self.ref,
            'value': value
        }

        await self._request('post', json=json)


def get_zwave_device(raw, control_data, request):
    device_type = raw['device_type_string']
    if device_type == DEVICE_ZWAVE_BATTERY:
        return ZWaveBattery(raw, control_data, request)
    elif device_type == DEVICE_ZWAVE_CENTRAL_SCENE:
        return ZWaveCentralScene(raw, control_data, request)
    elif device_type == DEVICE_ZWAVE_DOOR_LOCK:
        return ZwaveDoorLock(raw, control_data, request)
    elif device_type == DEVICE_ZWAVE_SENSOR_BINARY:
        return ZWaveSensorBinary(raw, control_data, request)
    elif device_type == DEVICE_ZWAVE_SWITCH:
        return ZWaveSwitch(raw, control_data, request)
    elif device_type == DEVICE_ZWAVE_SWITCH_BINARY:
        return ZWaveSwitch(raw, control_data, request)
    elif device_type == DEVICE_ZWAVE_SWITCH_MULTILEVEL:
        return ZWaveSwitchMultilevel(raw, control_data, request)
