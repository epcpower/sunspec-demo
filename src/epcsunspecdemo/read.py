import sys

import click

import epcsunspecdemo.clishared


@click.group(
    name='read',
    help='Read data points',
)
def group():
    pass


def common(device_factory, model_name, point_names):
    device = device_factory()
    model = device[model_name]

    if model is None:
        click.echo('No model found by the name {!r}'.format(model_name))

        click.echo(
            'Perhaps you meant one of: {}'.format(', '.join(device.models)),
        )

        sys.exit(1)

    model.read()

    show_all = len(point_names) == 0

    if show_all:
        point_names = model.points

    for point_name in point_names:
        click.echo('{}: {}'.format(point_name, model[point_name]))

    if show_all:
        for index, block in enumerate(model.repeating):
            if block is None:
                continue

            click.echo()
            click.echo('Repetition: {}'.format(index))

            for point_name in block.points:
                click.echo('    {}: {}'.format(point_name, block[point_name]))


commands = epcsunspecdemo.clishared.Commands.build(
    options=(
        epcsunspecdemo.clishared.model_name_option,
        epcsunspecdemo.clishared.point_names_option,
    ),
    common=common,
)
commands.add_to(group)
