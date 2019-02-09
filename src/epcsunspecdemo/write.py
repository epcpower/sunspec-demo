import sys

import click

import epcsunspecdemo.clishared


@click.group(
    name='write',
    help='Write data points',
)
def group():
    pass


converters = {
    'int16': int,
    'uint16': int,
    'int32': int,
    'uint32': int,
    'sunssf': None,
    'enum16': None,
    'bitfield32': None,
    'string': str,
    'acc16': None,
    'acc32': None,
    'pad': None,
}


def common(device_factory, model_name, point_names_and_values):
    device = device_factory()
    model = device[model_name]

    if model is None:
        click.echo('No model found by the name {!r}'.format(model_name))

        click.echo(
            'Perhaps you meant one of: {}'.format(', '.join(device.models)),
        )

        sys.exit(1)

    model.read()

    for point_name, value in point_names_and_values:
        sunspec_point_type = model.model.points[point_name].point_type.type
        converter = converters.get(sunspec_point_type)

        if converter is None:
            raise Exception()
        else:
            setattr(model, point_name, converter(value))
            model.model.points[point_name].write()


commands = epcsunspecdemo.clishared.Commands.build(
    options=(
        epcsunspecdemo.clishared.model_name_option,
        epcsunspecdemo.clishared.point_names_and_values_option,
    ),
    common=common,
)
commands.add_to(group)
