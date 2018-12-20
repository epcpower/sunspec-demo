import attr
import click

import epcsunspecdemo.demos


@attr.s
class Config:
    common = attr.ib(default=None)


@click.group()
@click.pass_context
def cli(context):
    context.obj = Config()


epcsunspecdemo.demos.add_commands(group=cli)
