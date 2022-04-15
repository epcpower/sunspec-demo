import attr
import click
import serial.tools.list_ports

# https://github.com/pallets/click/issues/646#issuecomment-435317967
import sunspecdemo.utils
sunspecdemo.utils.click_show_default_true()

import sunspecdemo.demos
import sunspecdemo.models
import sunspecdemo.read
import sunspecdemo.scan
import sunspecdemo.write
import sunspecdemo.datalogger


@attr.s
class Config:
    common = attr.ib(default=None)


@click.group()
@click.version_option(version=sunspecdemo.__version__)
@click.pass_context
def cli(context):
    context.obj = Config()


sunspecdemo.demos.add_commands(group=cli)
cli.add_command(sunspecdemo.models.get_models)
cli.add_command(sunspecdemo.scan.cli, name='scan')
cli.add_command(sunspecdemo.read.group)
cli.add_command(sunspecdemo.write.group)
cli.add_command(sunspecdemo.datalogger.group)


@cli.command(
    name='list-ports',
    help='List available serial ports',
)
def list_ports():
    for port in serial.tools.list_ports.comports():
        print(port)
