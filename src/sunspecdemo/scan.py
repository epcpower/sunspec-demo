import socket

import attr
import click

import sunspec.core.client

import sunspecdemo.utils


@attr.s
class SerialDeviceFactory:
    port = attr.ib()
    baudrate = attr.ib()
    timeout = attr.ib()

    def build(self, slave_id):
        return sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
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

    def build(self, slave_id):
        return sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            device_type=sunspec.core.client.TCP,
            ipaddr=self.address,
            ipport=self.port,
            timeout=self.timeout,
        )


@click.group(
    help='Scan for responding nodes',
)
def cli():
    pass


node_id_range_option = click.option(
    '--slave-id-range',
    type=(int, int),
    default=(1, 246),
    help='Node ID range to scan for converters',
)


@cli.command(
    help='Scan over Modbus RTU',
)
@sunspecdemo.clishared.serial_port_option
@sunspecdemo.clishared.serial_baudrate_option
@sunspecdemo.clishared.timeout_option
@sunspecdemo.clishared.model_path_option
@node_id_range_option
def serial(
        port,
        timeout,
        model_path,
        slave_id_range,
        baudrate,
):
    device_factory = SerialDeviceFactory(
        port=port,
        baudrate=baudrate,
        timeout=timeout,
    )

    common(
        device_factory=device_factory,
        model_path=model_path,
        slave_id_range=slave_id_range,
    )


@cli.command(
    help='Scan over Modbus TCP',
)
@sunspecdemo.clishared.tcp_address_option
@sunspecdemo.clishared.tcp_port_option
@sunspecdemo.clishared.timeout_option
@sunspecdemo.clishared.model_path_option
@node_id_range_option
def tcp(
        address,
        port,
        timeout,
        model_path,
        slave_id_range,
):
    device_factory = TcpDeviceFactory(
        address=address,
        port=port,
        timeout=timeout,
    )

    common(
        device_factory=device_factory,
        model_path=model_path,
        slave_id_range=slave_id_range,
    )


timeout_exceptions = (
    sunspec.core.client.SunSpecClientError,
    socket.timeout,
)


def common(
        device_factory,
        model_path,
        slave_id_range,
):
    found = []

    for slave_id in range(slave_id_range[0], slave_id_range[1] + 1):
        click.echo('-- Scanning node {}'.format(slave_id))
        with sunspecdemo.utils.fresh_smdx_path(model_path):
            try:
                device_factory.build(
                    slave_id=slave_id,
                )
            except timeout_exceptions as e:
                click.echo('   ' + str(e))
                continue

        click.echo('   Found')
        found.append(slave_id)

    if len(found) > 0:
        found_message = '{nodes} found at {ids} {list}'.format(
            nodes='Nodes' if len(found) > 1 else 'Node',
            ids='IDs' if len(found) > 1 else 'ID',
            list=', '.join(str(id) for id in found),
        )
    else:
        found_message = 'No nodes found'

    click.echo()
    click.echo()
    click.echo('Scan complete.  {}'.format(found_message))
