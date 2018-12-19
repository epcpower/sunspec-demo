import setuptools


setuptools.setup(
    name='epcsunspecdemo',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
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
                'gridtied = epcsunspecdemo.gridtied:entry_point',
                'dcdc = epcsunspecdemo.dcdc:entry_point',
            ),
        ],
    },
)
