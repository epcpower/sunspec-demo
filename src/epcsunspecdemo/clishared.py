import click


model_path_option = click.option(
    '--model-path',
    type=click.Path(file_okay=False),
    default='models',
    help='Path to the directory containing custom smdx_*.xml files',
)

