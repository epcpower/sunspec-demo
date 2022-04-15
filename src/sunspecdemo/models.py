import pathlib

import click
import requests

import sunspecdemo.clishared


smdx_file_template = 'smdx_{model_index:05}.xml'

url_template = (
    'https://raw.githubusercontent.com'
    '/epcpower/epcpower.github.io/master/release_artifacts'
    '/{version}'
    '/' + smdx_file_template
)


@click.command(
    name='get-models',
    help='Download EPC SMDX model definitions',
)
@click.option(
    '--version',
    default='1.2.5',
    help='Converter software version',
)
@click.option(
    '--model-index',
    'model_indexes',
    multiple=True,
    type=int,
    default=[65534],
    help='Model number to download',
)
@sunspecdemo.clishared.model_path_option
def get_models(version, model_indexes, model_path):
    version = version.split('.')

    model_path = pathlib.Path(model_path)
    model_path.mkdir(parents=True, exist_ok=True)

    for model_index in model_indexes:
        url = url_template.format(
            version='_'.join(version),
            model_index=model_index,
        )

        smdx_file_name = smdx_file_template.format(model_index=model_index)

        response = requests.get(url)
        file = model_path/smdx_file_name
        file.write_bytes(response.content)
        click.echo('Saved {}'.format(smdx_file_name))
