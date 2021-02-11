import attr
import click
import serial.tools.list_ports

# https://github.com/pallets/click/issues/646#issuecomment-435317967
import epcsunspecdemo.utils
epcsunspecdemo.utils.click_show_default_true()

import epcsunspecdemo.demos
import epcsunspecdemo.models
import epcsunspecdemo.read
import epcsunspecdemo.scan
import epcsunspecdemo.write
import epcsunspecdemo.datalogger


@attr.s
class Config:
    common = attr.ib(default=None)


@click.group()
@click.version_option(version=epcsunspecdemo.__version__)
@click.pass_context
def cli(context):
    context.obj = Config()


epcsunspecdemo.demos.add_commands(group=cli)
cli.add_command(epcsunspecdemo.models.get_models)
cli.add_command(epcsunspecdemo.scan.cli, name='scan')
cli.add_command(epcsunspecdemo.read.group)
cli.add_command(epcsunspecdemo.write.group)
cli.add_command(epcsunspecdemo.datalogger.group)


@cli.command(
    name='list-ports',
    help='List available serial ports',
)
def list_ports():
    for port in serial.tools.list_ports.comports():
        print(port)
