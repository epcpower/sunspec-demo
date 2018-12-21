import sys

import click
import serial.serialutil


model_path_option = click.option(
    '--model-path',
    type=click.Path(file_okay=False),
    default='models',
    help='Path to the directory containing custom smdx_*.xml files',
)


timeout_option = click.option(
    '--timeout',
    default=0.1,
    help='Modbus communication timeout in seconds',
)


if sys.platform.startswith('win'):
    port_help = 'Name of the COM port'
else:
    port_help = 'Path to the serial device'


serial_port_option = click.option(
    '--port',
    required=True,
    help=port_help,
)


serial_baudrate_option = click.option(
    '--baudrate',
    type=click.Choice(
        str(rate)
        for rate in serial.serialutil.SerialBase.BAUDRATES
    ),
    default='9600',
    help='Serial baudrate',
)


tcp_address_option = click.option(
    '--address',
    required=True,
    help='The IP address or host name of the converter',
)


tcp_port_option = click.option(
    '--port',
    type=int,
    default=502,
    help='The TCP port on the converter',
)
