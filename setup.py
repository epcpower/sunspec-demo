import os
import setuptools


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as file:
        return file.read()


setuptools.setup(
    name='epcsunspecdemo',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'click',
        'pysunspec',
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
