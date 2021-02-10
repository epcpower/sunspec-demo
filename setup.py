import os
import setuptools


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as file:
        return file.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name='epcsunspecdemo',
    version=get_version('./src/epcsunspecdemo/_version.py'),
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'attrs',
        'click',
        'pysunspec',
        'toolz',
        'tqdm',
    ],
    extras_require={
        'development': [
            'gitignoreio',
        ],
    },
    entry_points={
        'console_scripts': [
            (
                'epcsunspecdemo = epcsunspecdemo.cli:cli',
            ),
        ],
    },
)
