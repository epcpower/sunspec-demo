import sys

import click

import sunspecdemo.clishared


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
        points = {}
        points.update(model.model.points)
        points.update(model.model.points_sf)
    else:
        points = {
            point_name: model.model.points.get(
                point_name,
                model.model.points_sf.get(point_name),
            )
            for point_name in point_names
        }

    for point_name, point in points.items():
        click.echo('{}: {}'.format(
            point_name,
            point.value,
        ))

    if show_all:
        for index, block in enumerate(model.repeating):
            if block is None:
                continue

            click.echo()
            click.echo('Repetition: {}'.format(index))

            for point_name in block.points:
                point = block.block.points[point_name]
                click.echo('    {}: {}'.format(point_name, point.value))


commands = sunspecdemo.clishared.Commands.build(
    options=(
        sunspecdemo.clishared.model_name_option,
        sunspecdemo.clishared.point_names_option,
    ),
    common=common,
)
commands.add_to(group)
