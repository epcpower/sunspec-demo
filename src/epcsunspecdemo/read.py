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

    if len(point_names) == 0:
        point_names = model.points

    for point_name in point_names:
        print('{}: {}'.format(point_name, model[point_name]))


commands = epcsunspecdemo.clishared.Commands.build(
    options=(
        epcsunspecdemo.clishared.model_name_option,
        epcsunspecdemo.clishared.point_names_option,
    ),
    common=common,
)
commands.add_to(group)
