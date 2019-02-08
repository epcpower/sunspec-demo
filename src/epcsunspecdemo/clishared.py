import sys

import attr
import click
import serial.serialutil
import sunspec.core.client

import epcsunspecdemo.utils


model_path_option = click.option(
    '--model-path',
    type=click.Path(file_okay=False),
    default='models',
    help='Path to the directory containing custom smdx_*.xml files',
)


timeout_option = click.option(
    '--timeout',
    default=1,
    type=float,
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


slave_id_option = click.option(
    '--slave-id',
    type=int,
    default=1,
    help='Node ID of the converter',
)


model_name_option = click.option(
    '--model-name',
    required=True,
    help='The name of the model',
)


point_names_option = click.option(
    '--point-name',
    'point_names',
    multiple=True,
    help='The name of the point',
)


@attr.s
class RtuDeviceFactory:
    port = attr.ib()
    baudrate = attr.ib()
    timeout = attr.ib()
    slave_id = attr.ib()
    model_path = attr.ib()

    def __call__(self):
        with epcsunspecdemo.utils.fresh_smdx_path(self.model_path):
            return sunspec.core.client.SunSpecClientDevice(
                slave_id=self.slave_id,
                device_type=sunspec.core.client.RTU,
                name=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )


@attr.s
class TcpDeviceFactory:
    address = attr.ib()
    port = attr.ib()
    timeout = attr.ib()
    slave_id = attr.ib()
    model_path = attr.ib()

    def __call__(self):
        with epcsunspecdemo.utils.fresh_smdx_path(self.model_path):
            return sunspec.core.client.SunSpecClientDevice(
                slave_id=self.slave_id,
                device_type=sunspec.core.client.TCP,
                ipaddr=self.address,
                ipport=self.port,
                timeout=self.timeout,
            )


@attr.s
class Commands:
    rtu = attr.ib()
    tcp = attr.ib()

    @classmethod
    def build(cls, options, common):
        common_options = (
            epcsunspecdemo.clishared.timeout_option,
            epcsunspecdemo.clishared.slave_id_option,
            epcsunspecdemo.clishared.model_path_option,
        )

        @click.command()
        @epcsunspecdemo.utils.apply_decorators(options)
        @serial_port_option
        @serial_baudrate_option
        @epcsunspecdemo.utils.apply_decorators(common_options)
        def rtu(port, baudrate, timeout, slave_id, model_path, **kwargs):
            device_factory = RtuDeviceFactory(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                slave_id=slave_id,
                model_path=model_path,
            )

            common(
                device_factory=device_factory,
                **kwargs
            )

        @click.command()
        @epcsunspecdemo.utils.apply_decorators(options)
        @tcp_address_option
        @tcp_port_option
        @epcsunspecdemo.utils.apply_decorators(common_options)
        def tcp(address, port, timeout, slave_id, model_path, **kwargs):
            device_factory = TcpDeviceFactory(
                address=address,
                port=port,
                timeout=timeout,
                slave_id=slave_id,
                model_path=model_path,
            )

            common(
                device_factory=device_factory,
                **kwargs
            )

        return cls(rtu=rtu, tcp=tcp)

    def add_to(self, group):
        for command in (self.rtu, self.tcp):
            group.add_command(command)
