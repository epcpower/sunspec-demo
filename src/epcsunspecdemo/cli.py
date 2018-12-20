import attr
import click
import sunspec.core.client

import epcsunspecdemo.demos


@attr.s
class Config:
    common = attr.ib(default=None)


@click.group()
@click.pass_context
def cli(context):
    context.obj = Config()


@cli.group()
@click.pass_obj
def gridtied(config):
    config.common = epcsunspecdemo.demos.gridtied


@cli.group()
@click.pass_obj
def dcdc(config):
    config.common = epcsunspecdemo.demos.dcdc


models_option = click.option(
    '--models',
    type=click.Path(file_okay=False),
    default='models',
)
invert_enable_option = click.option('--invert-enable/--no-invert-enable')
slave_id_option = click.option('--slave-id', type=int, default=1)
max_count_option = click.option('--max-count', type=int, default=100)
cycles_option = click.option('--cycles', type=int, default=25)


@click.command()
@click.option('--port', required=True)
@click.option('--baudrate', type=int, default=9600)
@models_option
@invert_enable_option
@slave_id_option
@max_count_option
@cycles_option
@click.pass_obj
def serial(
        config,
        port,
        models,
        invert_enable,
        slave_id,
        max_count,
        baudrate,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(models):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            max_count=max_count,
            device_type=sunspec.core.client.RTU,
            name=port,
            baudrate=baudrate,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


@click.command()
@click.option('--ip')
@models_option
@invert_enable_option
@slave_id_option
@max_count_option
@cycles_option
@click.pass_obj
def tcp(
        config,
        ip,
        models,
        invert_enable,
        slave_id,
        max_count,
        cycles,
):
    with epcsunspecdemo.utils.fresh_smdx_path(models):
        device = sunspec.core.client.SunSpecClientDevice(
            slave_id=slave_id,
            max_count=max_count,
            device_type=sunspec.core.client.TCP,
            ipaddr=ip,
        )

    config.common(
        device=device,
        invert_enable=invert_enable,
        cycles=cycles,
    )


for group in (gridtied, dcdc):
    group.add_command(serial, name='serial')
    group.add_command(tcp, name='tcp')
