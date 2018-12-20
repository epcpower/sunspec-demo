import attr
import click
import serial.tools.list_ports

import epcsunspecdemo.demos


@attr.s
class Config:
    common = attr.ib(default=None)


@click.group()
@click.pass_context
def cli(context):
    context.obj = Config()


epcsunspecdemo.demos.add_commands(group=cli)


@cli.command(name='list-ports')
def list_ports():
    for port in serial.tools.list_ports.comports():
        print(port)
