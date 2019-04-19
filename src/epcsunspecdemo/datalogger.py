import itertools
import sys
import time

import click
import toolz
import tqdm

import epcsunspecdemo.clishared


@click.group(
    name='datalogger',
    help='Access the high speed data logger',
)
def group():
    pass


def terminate_on_model_failure(device, model, name):
    if model is None:
        click.echo('No model found by the name {!r}'.format(name))

        click.echo(
            'Perhaps you meant one of: {}'.format(', '.join(device.models)),
        )

        sys.exit(1)


def read(registers_per_read, log_model, total_octets):
    total_16_bit_bytes, remainder = divmod(total_octets, 2)

    offset = 0
    while offset < total_16_bit_bytes:
        log_model.Offset = offset
        log_model.model.points['Offset'].write()
        log_model.read()

        registers_to_read = min(
            registers_per_read,
            total_16_bit_bytes - offset,
        )

        yield from itertools.chain.from_iterable(
            getattr(log_model, 'R{:03}'.format(n)).to_bytes(
                2,
                byteorder='big',
                signed=False,
            )
            for n in range(registers_to_read)
        )

        offset += registers_to_read


def common(device_factory, registers_per_read, log_file):
    device = device_factory()

    configuration_model_name = 'data_logger'
    configuration_model = device[configuration_model_name]
    terminate_on_model_failure(
        device=device,
        model=configuration_model,
        name=configuration_model_name
    )

    log_model_name = 'data_logger_log'
    log_model = device[log_model_name]
    terminate_on_model_failure(
        device=device,
        model=log_model,
        name=log_model_name
    )

    configuration_model.read()

    while configuration_model.RdblOct == 0:
        print('Waiting for readable data...')
        time.sleep(1)
        configuration_model.read()

    total_octets = configuration_model.RdblOct

    bytes_iterable = read(
        registers_per_read=registers_per_read,
        log_model=log_model,
        total_octets=total_octets,

    )
    tqdm_iterable = tqdm.tqdm(
        iterable=bytes_iterable,
        total=total_octets,
        unit='b',
        unit_scale=True,
        unit_divisor=1024,
    )

    for block in toolz.partition_all(1024, tqdm_iterable):
        log_file.write(bytes(block))


commands = epcsunspecdemo.clishared.Commands.build(
    options=(
        click.option(
            '--registers-per-read',
            default=120,
            type=click.IntRange(min=1, max=123),
        ),
        click.option(
            '--log-file',
            required=True,
            type=click.File(mode='wb', atomic=True),
        )
    ),
    common=common,
)
commands.add_to(group)
