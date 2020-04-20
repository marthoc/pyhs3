"""Constants used in pyhs3."""

import logging

_LOGGER = logging.getLogger(__name__)

DEFAULT_ASCII_PORT = 11000
DEFAULT_HTTP_PORT = 80
DEFAULT_HTTP_TIMEOUT = 3
DEFAULT_PASSWORD = "default"
DEFAULT_USERNAME = "default"

DEVICE_ZWAVE_BARRIER_OPERATOR = "Z-Wave Barrier Operator"
DEVICE_ZWAVE_BATTERY = "Z-Wave Battery"
DEVICE_ZWAVE_CENTRAL_SCENE = "Z-Wave Central Scene"
DEVICE_ZWAVE_DOOR_LOCK = "Z-Wave Door Lock"
DEVICE_ZWAVE_FAN_STATE = "Z-Wave Fan State"
DEVICE_ZWAVE_LUMINANCE = "Z-Wave Luminance"
DEVICE_ZWAVE_OPERATING_STATE = "Z-Wave Operating State"
DEVICE_ZWAVE_RELATIVE_HUMIDITY = "Z-Wave Relative Humidity"
DEVICE_ZWAVE_SENSOR_BINARY = "Z-Wave Sensor Binary"
DEVICE_ZWAVE_SWITCH = "Z-Wave Switch"
DEVICE_ZWAVE_SWITCH_BINARY = "Z-Wave Switch Binary"
DEVICE_ZWAVE_SWITCH_MULTILEVEL = "Z-Wave Switch Multilevel"
DEVICE_ZWAVE_TEMPERATURE = "Z-Wave Temperature"

REASON_DISCONNECTED = "disconnected"
REASON_RECONNECTED = "reconnected"

STATE_CLOSED = "closed"
STATE_CLOSING = "closing"
STATE_CONNECTING = "connecting"
STATE_DISCONNECTED = "disconnected"
STATE_IDLE = "idle"
STATE_LISTENING = "listening"
STATE_OPEN = "open"
STATE_OPENING = "opening"
STATE_STOPPED = "stopped"
