import decimal
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
    'int16': decimal.Decimal,
    'uint16': decimal.Decimal,
    'int32': decimal.Decimal,
    'uint32': decimal.Decimal,
    'sunssf': None,
    'enum16': None,
    'bitfield32': None,
    'string': str,
    'acc16': None,
    'acc32': None,
    'pad': None,
}


def common(
        device_factory,
        model_name,
        point_names_and_values,
        repeating_point_names_and_values,
):
    device = device_factory()
    model = device[model_name]

    if model is None:
        click.echo('No model found by the name {!r}'.format(model_name))

        click.echo(
            'Perhaps you meant one of: {}'.format(', '.join(device.models)),
        )

        sys.exit(1)

    model.read()

    all_points = [
        (0, name, value)
        for name, value in point_names_and_values
    ]
    all_points.extend(repeating_point_names_and_values)

    for block_index, point_name, value in all_points:
        client_point = model.model.blocks[block_index].points[point_name]
        sunspec_point_type = client_point.point_type.type

        converter = converters.get(sunspec_point_type)

        if converter is None:
            raise Exception()
        else:
            client_point.value = converter(value)
            client_point.write()


commands = epcsunspecdemo.clishared.Commands.build(
    options=(
        epcsunspecdemo.clishared.repeating_point_names_and_values_option,
        epcsunspecdemo.clishared.model_name_option,
        epcsunspecdemo.clishared.point_names_and_values_option,
    ),
    common=common,
)
commands.add_to(group)
